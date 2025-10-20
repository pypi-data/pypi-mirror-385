from __future__ import annotations

import atexit
import json
import logging
import os
import re
import shutil
import tempfile
import time
import uuid
from io import BytesIO
from typing import Callable

from dotenv import find_dotenv, load_dotenv
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from edu_agents.core.api_key_manager import get_async_openai_client
from utils.supabase_utils import upload_image_to_supabase

load_dotenv(find_dotenv())

logger = logging.getLogger(__name__)

# Default animation duration for fallback scenarios
DEFAULT_ANIMATION_DURATION = 10.0  # seconds

# Optimal FPS for clean frame durations (50ms per frame)
GIF_ANIMATION_FPS = 20

def _analyze_animation_duration(driver) -> float:
    """
    Analyze the HTML/CSS/JS to determine the total animation duration.
    Uses a simple regex-based approach to avoid DOM interference.
    
    Parameters
    ----------
    driver : webdriver.Chrome
        The Selenium WebDriver instance
        
    Returns
    -------
    float
        The total duration in seconds
    """
    try:
        # Get page source for regex-based analysis (safer than DOM manipulation)
        page_source = driver.page_source
        
        # Extract JavaScript constants
        constants = {}
        
        # Find const declarations with various patterns
        const_patterns = [
            r'const\s+(\w+)\s*=\s*(\d+)',  # const name = number
            r'const\s+(\w+)\s*=\s*([^;]+);'  # const name = expression
        ]
        
        for pattern in const_patterns:
            matches = re.findall(pattern, page_source)
            for match in matches:
                name, value = match
                try:
                    # Try to evaluate simple expressions
                    if value.isdigit():
                        constants[name] = int(value)
                    else:
                        # Replace known constants in expressions
                        eval_value = value
                        for const_name, const_val in constants.items():
                            eval_value = re.sub(rf'\b{const_name}\b', str(const_val), eval_value)
                        
                        # Handle simple arithmetic
                        if re.match(r'^[\d\s+\-*/()\s]+$', eval_value):
                            constants[name] = eval(eval_value)
                        else:
                            # Extract just the first number if complex
                            num_match = re.search(r'\d+', value)
                            if num_match:
                                constants[name] = int(num_match.group())
                except Exception as e:
                    logger.warning(f"Failed to evaluate constant '{name}': {e}")
                    pass
        
        # Find setTimeout calls and extract delays more comprehensively
        timeouts = []
        
        # More comprehensive patterns for setTimeout calls
        timeout_patterns = [
            r'setTimeout\s*\([^,]*,\s*(\w+)\s*\)',  # setTimeout(..., variable)
            r'setTimeout\s*\([^,]*,\s*(\d+)\s*\)',  # setTimeout(..., number)
            r'setTimeout\s*\([^,]*,\s*([^)]+)\)',   # setTimeout(..., expression)
        ]
        
        for pattern in timeout_patterns:
            matches = re.findall(pattern, page_source)
            for match in matches:
                try:
                    if match.isdigit():
                        timeouts.append(int(match))
                    elif match in constants:
                        timeouts.append(constants[match])
                    else:
                        # Try to evaluate expression with known constants
                        eval_expr = match
                        for const_name, const_val in constants.items():
                            eval_expr = re.sub(rf'\b{const_name}\b', str(const_val), eval_expr)
                        
                        # Handle complex expressions like stepDelay*3
                        if re.match(r'^[\d\s+\-*/()\s]+$', eval_expr):
                            result = eval(eval_expr)
                            timeouts.append(result)
                except Exception as e:
                    logger.warning(f"Failed to evaluate timeout expression '{match}': {e}")
                    pass
        
        # Also look for expressions like "initialDelay + stepDelay*3" in the code
        # These often appear in the final setTimeout calls
        complex_timing_patterns = [
            r'(\w+\s*\+\s*\w+\s*\*\s*\d+)',  # var + var*number
            r'(\w+\s*\+\s*\w+\s*\*\s*\w+)',  # var + var*var
        ]
        
        for pattern in complex_timing_patterns:
            matches = re.findall(pattern, page_source)
            for match in matches:
                try:
                    eval_expr = match
                    for const_name, const_val in constants.items():
                        eval_expr = re.sub(rf'\b{const_name}\b', str(const_val), eval_expr)
                    
                    if re.match(r'^[\d\s+\-*/()\s]+$', eval_expr):
                        result = eval(eval_expr)
                        timeouts.append(result)
                except Exception as e:
                    logger.warning(f"Failed to evaluate complex timing expression '{match}': {e}")
                    pass
        
        # Special handling for forEach loops with timing calculations
        # Look for patterns like: forEach((item, idx) => { ... setTimeout(..., delay_expression) })
        foreach_patterns = [
            r'forEach\s*\([^{]*\{[^}]*setTimeout[^}]*\}[^}]*\)',  # forEach with setTimeout inside
        ]
        
        for pattern in foreach_patterns:
            matches = re.findall(pattern, page_source, re.DOTALL)
            for match in matches:
                # Look for timing calculations inside the forEach
                # Pattern: variable = expression involving idx
                timing_calc_patterns = [
                    r'(\w+)\s*=\s*(\w+\s*\+\s*\w+\s*\*\s*\w+)',
                    r'(\w+)\s*=\s*(\w+\s*\+\s*\w+\s*\*\s*\d+)',
                ]
                
                for calc_pattern in timing_calc_patterns:
                    calc_matches = re.findall(calc_pattern, match)
                    for calc_match in calc_matches:
                        var_name, expression = calc_match
                        try:
                            # For forEach loops, we need to estimate the maximum idx
                            # Look for the array being iterated over
                            array_patterns = [
                                r'(\w+)\.forEach',  # arrayName.forEach
                                r'querySelectorAll\([^)]+\)\.forEach',  # DOM query forEach
                            ]
                            
                            max_iterations = 4  # Default assumption for educational animations
                            
                            # Try to find the actual array size
                            for array_pattern in array_patterns:
                                array_matches = re.findall(array_pattern, page_source)
                                if array_matches:
                                    # Count how many elements are being selected
                                    if 'querySelectorAll' in match:
                                        # Look for class or tag counts in HTML
                                        selector_match = re.search(
                                            r'querySelectorAll\([\'"]([^\'"]+)[\'"]\)', match
                                        )
                                        if selector_match:
                                            selector = selector_match.group(1)
                                            # Count occurrences of this selector in HTML
                                            if selector.startswith('.'):
                                                class_name = selector[1:]
                                                element_count = len(re.findall(rf'class=[\'"][^\'"\s]*{class_name}[^\'"\s]*[\'"]', page_source)) # noqa E501
                                                if element_count > 0:
                                                    max_iterations = element_count
                            
                            # Calculate timing for each iteration
                            for idx in range(max_iterations):
                                eval_expr = expression
                                eval_expr = re.sub(r'\bidx\b', str(idx), eval_expr)
                                eval_expr = re.sub(r'\bi\b', str(idx), eval_expr)
                                
                                for const_name, const_val in constants.items():
                                    eval_expr = re.sub(
                                        rf'\b{const_name}\b', str(const_val), eval_expr
                                    )
                                
                                if re.match(r'^[\d\s+\-*/()\s]+$', eval_expr):
                                    result = eval(eval_expr)
                                    timeouts.append(result)
                                    
                        except Exception as e:
                            logger.warning(f"Failed to evaluate forEach timing '{expression}': {e}")
                            pass
        
        # Find CSS animation/transition durations 
        css_durations = []
        
        # Look for transition durations
        transition_matches = re.findall(r'transition[^;]*?(\d+(?:\.\d+)?)s', page_source)
        for match in transition_matches:
            css_durations.append(float(match))
        
        # Look for animation durations (including @keyframes)
        animation_matches = re.findall(r'animation[^;]*?(\d+(?:\.\d+)?)s', page_source)
        for match in animation_matches:
            css_durations.append(float(match))
        
        # Look for @keyframes animation durations in CSS
        keyframe_matches = re.findall(
            r'@keyframes[^{]*{[^}]*}[^{]*animation[^;]*?(\d+(?:\.\d+)?)s', page_source, re.DOTALL
        )
        for match in keyframe_matches:
            css_durations.append(float(match))
        
        # Calculate final duration
        max_js_timeout = max(timeouts) / 1000.0 if timeouts else 0  # Convert to seconds
        max_css_duration = max(css_durations) if css_durations else 0
        
        # For complex animations, we need to account for:
        # 1. The longest setTimeout delay
        # 2. Any CSS animations that might run after that
        # 3. A buffer for sparkle/final effects
        sparkle_buffer = 2.0  # Extra time for sparkle animations and completion
        
        final_duration = max(
            max_css_duration,
            max_js_timeout + max_css_duration + sparkle_buffer
        )
        
        logger.info(f"Duration analysis: JS timeouts={timeouts}, CSS durations={css_durations}")
        logger.info(f"Max JS timeout: {max_js_timeout}s, Max CSS: {max_css_duration}s")
        
        return final_duration
        
    except Exception as e:
        logger.error(f"Error in regex-based duration analysis: {e}")
        # Return a safe default duration
        return DEFAULT_ANIMATION_DURATION

def _calculate_optimal_fps(duration: float) -> tuple[int, int]:
    """
    Calculate the optimal FPS and total frames to ensure we capture exactly one animation cycle.
    
    Parameters
    ----------
    duration : float
        The duration of the animation in seconds
        
    Returns
    -------
    tuple[int, int]
        The optimal FPS and total number of frames
    """
    # Calculate total frames needed
    total_frames = int(duration * GIF_ANIMATION_FPS)
    
    return GIF_ANIMATION_FPS, total_frames

def _create_gif_from_frames(frames: list[Image.Image], duration: float, fps: int) -> bytes:
    """
    Create an animated GIF from captured frames.
    
    Parameters
    ----------
    frames : list[Image.Image]
        List of frames as PIL Images
    duration : float
        Total duration of the animation in seconds
    fps : int
        Frames per second used during capture (should match OPTIMAL_FPS)
        
    Returns
    -------
    bytes
        The GIF file as bytes
    """
    if not frames:
        raise ValueError("No frames provided")
    
    # Calculate exact frame duration in milliseconds using global FPS
    frame_duration = int(1000 / GIF_ANIMATION_FPS)
    
    # Log timing details
    logger.info("GIF creation details:")
    logger.info(f"  Frame duration: {frame_duration}ms")
    logger.info(f"  Total frames: {len(frames)}")
    logger.info(f"  Total duration: {(frame_duration * len(frames))/1000:.3f}s")
    logger.info(f"  Target duration: {duration:.3f}s")
    
    # Save frames as GIF
    output = BytesIO()
    frames[0].save(
        output,
        format='GIF',
        append_images=frames[1:],
        save_all=True,
        duration=frame_duration,
        loop=0  # Loop forever
    )
    return output.getvalue()

def _capture_animation_frames(html_code: str) -> tuple[list[Image.Image], float, int]:
    """
    Capture frames of the HTML animation using Selenium.
    
    Parameters
    ----------
    html_code : str
        The HTML animation code
        
    Returns
    -------
    tuple[list[Image.Image], float, int]
        List of captured frames as PIL Images, the animation duration in seconds,
        and the FPS used for capture
    """
    # Set up Chrome in headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--force-device-scale-factor=1")
    chrome_options.add_argument("--hide-scrollbars")
    chrome_options.add_argument("--window-size=1200,1200")
    
    # Server-specific options to prevent conflicts
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--no-default-browser-check")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    
    # Use a unique temporary user data directory
    temp_user_data_dir = tempfile.mkdtemp(prefix=f"chrome_user_data_{uuid.uuid4().hex[:8]}_")
    chrome_options.add_argument(f"--user-data-dir={temp_user_data_dir}")
    
    # Add cleanup for the temp directory
    atexit.register(lambda: shutil.rmtree(temp_user_data_dir, ignore_errors=True))
    
    # Create a temporary HTML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        # Add viewport meta tag and size control styles
        head_content = """
        <meta name="viewport" content="width=1024, height=1024, initial-scale=1.0,
        maximum-scale=1.0, user-scalable=no">
        <style>
        html, body {
            width: 1024px !important;
            height: 1024px !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
        }
        .animation-container {
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            width: 1024px !important;
            height: 1024px !important;
            margin: 0 !important;
            padding: 10px !important;
            box-sizing: border-box !important;
        }
        </style>
        """
        
        # Add animation control script
        control_script = """
        <script>
        // Animation state tracking
        window.animationState = {
            started: false,
            startTime: null,
            ready: false,
            originalTimeouts: [],
            pausedTimeouts: []
        };
        
        // Override setTimeout to capture and control JavaScript animations
        const originalSetTimeout = window.setTimeout;
        window.setTimeout = function(callback, delay, ...args) {
            if (window.animationState.started) {
                // Animation has started, use normal setTimeout
                return originalSetTimeout(callback, delay, ...args);
            } else {
                // Animation not started yet, store the timeout for later execution
                const timeoutInfo = {
                    callback: callback,
                    delay: delay,
                    args: args,
                    id: Date.now() + Math.random() // Unique ID
                };
                window.animationState.pausedTimeouts.push(timeoutInfo);
                return timeoutInfo.id;
            }
        };
        
        // Override clearTimeout to handle our paused timeouts
        const originalClearTimeout = window.clearTimeout;
        window.clearTimeout = function(id) {
            // Remove from paused timeouts if it exists there
            const index = window.animationState.pausedTimeouts.findIndex(t => t.id === id);
            if (index >= 0) {
                window.animationState.pausedTimeouts.splice(index, 1);
                return;
            }
            // Otherwise use original clearTimeout
            return originalClearTimeout(id);
        };
        
        // Function to pause all animations (CSS and JS)
        function pauseAnimations() {
            // Pause CSS animations
            document.body.style.setProperty('animation-play-state', 'paused', 'important');
            document.querySelectorAll('*').forEach(element => {
                element.style.setProperty('animation-play-state', 'paused', 'important');
            });
            // JS animations are already paused by our setTimeout override
        }
        
        // Function to start all animations with precise timing
        function startAnimations() {
            return new Promise((resolve) => {
                // Record the exact start time
                window.animationState.startTime = performance.now();
                window.animationState.started = true;
                
                // Start CSS animations
                document.body.style.setProperty('animation-play-state', 'running', 'important');
                document.querySelectorAll('*').forEach(element => {
                    element.style.setProperty('animation-play-state', 'running', 'important');
                    // Reset CSS animations to start
                    const animations = element.getAnimations();
                    animations.forEach(animation => {
                        animation.startTime = document.timeline.currentTime;
                    });
                });
                
                // Start JavaScript animations (execute all paused timeouts)
                const startTime = performance.now();
                window.animationState.pausedTimeouts.forEach(timeoutInfo => {
                    originalSetTimeout(() => {
                        timeoutInfo.callback.apply(null, timeoutInfo.args);
                    }, timeoutInfo.delay);
                });
                window.animationState.pausedTimeouts = []; // Clear the paused timeouts
                
                // Wait for next animation frame to ensure rendering has started
                requestAnimationFrame(() => {
                    requestAnimationFrame(() => {
                        window.animationState.ready = true;
                        resolve();
                    });
                });
            });
        }
        
        // Function to check if animations are ready for capture
        function isAnimationReady() {
            return window.animationState.ready;
        }
        
        // Function to get current animation progress
        function getAnimationProgress() {
            if (!window.animationState.started) return null;
            const currentTime = performance.now();
            const elapsed = (currentTime - window.animationState.startTime) / 1000; // Convert to s
            return {
                started: window.animationState.started,
                ready: window.animationState.ready,
                startTime: window.animationState.startTime,
                currentTime: currentTime,
                elapsedSeconds: elapsed,
                pausedTimeouts: window.animationState.pausedTimeouts.length
            };
        }
        
        // Function to enforce viewport and container size
        function enforceSize() {
            document.documentElement.style.cssText = `
                width: 1024px !important;
                height: 1024px !important;
                margin: 0 !important;
                padding: 0 !important;
                overflow: hidden !important;
            `;
            
            document.body.style.cssText = `
                width: 1024px !important;
                height: 1024px !important;
                margin: 0 !important;
                padding: 0 !important;
                overflow: hidden !important;
                display: block !important;
            `;
            
            const container = document.querySelector('.animation-container');
            if (container) {
                container.style.cssText = `
                    position: absolute !important;
                    top: 0 !important;
                    left: 0 !important;
                    width: 1024px !important;
                    height: 1024px !important;
                    margin: 0 !important;
                    padding: 10px !important;
                    box-sizing: border-box !important;
                `;
            }
        }
        
        // Initialize on load - this runs BEFORE the original script
        document.addEventListener('DOMContentLoaded', () => {
            enforceSize();
            pauseAnimations();
        });
        window.addEventListener('load', () => {
            enforceSize();
            pauseAnimations();
        });
        </script>
        """
        
        # Add content to HTML
        if '<head>' in html_code:
            html_code = html_code.replace('<head>', f'<head>{head_content}{control_script}')
        else:
            html_code = f'<head>{head_content}{control_script}</head>{html_code}'
            
        f.write(html_code)
        temp_html_path = f.name
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(f"file://{temp_html_path}")
        
        # Set viewport size
        driver.set_window_rect(width=1024, height=1024)
        
        # Force exact viewport size using CDP
        driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {
            'width': 1024,
            'height': 1024,
            'deviceScaleFactor': 1,
            'mobile': False
        })
        
        # Wait for page load and ensure animations are paused
        time.sleep(0.5)
        
        # Get animation duration BEFORE we start interfering with the page
        duration = _analyze_animation_duration(driver)
        logger.info(f"Detected animation duration: {duration} seconds")
        
        # Safety check: ensure we have a reasonable duration
        if duration <= 0:
            logger.warning("Detected duration is 0 or negative, using fallback duration")
            duration = DEFAULT_ANIMATION_DURATION
        
        # Calculate optimal FPS and frame count
        fps, total_frames = _calculate_optimal_fps(duration)
        frame_delay = duration / total_frames  # Exact delay between frames
        
        logger.info(f"Capturing {total_frames} frames with {frame_delay:.3f}s delay")
        
        # Start capturing frames
        frames = []
        
        # Start the animations and wait for them to be ready
        logger.info("Starting animations and waiting for readiness...")
        driver.execute_script("return startAnimations();")  # This returns a promise
        
        # Poll until animations are ready
        max_wait_time = 5.0  # Maximum 5 seconds to wait
        start_wait = time.time()
        while time.time() - start_wait < max_wait_time:
            ready = driver.execute_script("return isAnimationReady();")
            if ready:
                break
            time.sleep(0.01)  # Check every 10ms
        else:
            raise Exception("Animations failed to start within timeout")
        
        # Get the precise animation start time from the browser
        _ = driver.execute_script("return getAnimationProgress();")
        
        # Start our capture timing from this point
        capture_start = time.time()
        
        for frame in range(total_frames):
            # Calculate exact time this frame should be captured
            target_time = capture_start + (frame * frame_delay)
            
            # Wait until it's time to capture this frame
            now = time.time()
            if now < target_time:
                time.sleep(target_time - now)
            
            # Get screenshot with exact dimensions
            png_data = driver.get_screenshot_as_png()
            image = Image.open(BytesIO(png_data))
            
            # Verify image dimensions
            if image.size != (1024, 1024):
                raise Exception(
                    f"Screenshot dimensions incorrect: got {image.size}, expected (1024, 1024)"
                )
            
            frames.append(image)
        
        actual_duration = time.time() - capture_start
        logger.info(f"Captured {len(frames)} frames in {actual_duration:.2f}s")
        
        return frames, duration, fps
        
    finally:
        try:
            driver.quit()
        except Exception as e:
            logger.warning(f"Failed to quit driver: {e}")
            pass
        try:
            os.remove(temp_html_path)
        except Exception as e:
            logger.warning(f"Failed to remove temporary HTML file: {e}")
            pass
        try:
            # Clean up the temporary user data directory
            shutil.rmtree(temp_user_data_dir, ignore_errors=True)
        except Exception as e:
            logger.warning(f"Failed to remove temporary user data directory: {e}")
            pass

def _clean_html_code(html_code: str) -> str:
    """
    Clean the HTML code to remove any unnecessary boilerplate.
    """
    cleaned_html_code = html_code.replace("```html", "").replace("```", "")
    # remove all content between <!-- and -->
    cleaned_html_code = re.sub(r'<!--.*?-->', '', cleaned_html_code, flags=re.DOTALL)
    # remove all content before the <!DOCTYPE html> tag, but not the <!DOCTYPE html> tag itself
    cleaned_html_code = re.sub(r'^.*?<!DOCTYPE html>', '<!DOCTYPE html>', cleaned_html_code, 
                        flags=re.DOTALL)
    # remove all content after the </html> tag, but not the </html> tag itself
    cleaned_html_code = re.sub(r'</html>.*', '</html>', cleaned_html_code, flags=re.DOTALL)
    return cleaned_html_code

async def _generate_animation_html(prompt: str) -> str:
    """
    Generate HTML/CSS/JS animation code using GPT-4.
    
    Parameters
    ----------
    prompt : str
        Description of the animation to generate
        
    Returns
    -------
    str
        The complete HTML code including CSS and JavaScript
    """
    try:
        system_prompt = """You are an expert at creating HTML/CSS/JS animations with a focus on 
        educational clarity and visual precision. Create a self-contained HTML file that includes
        all necessary CSS and JavaScript inline. Follow these guidelines strictly:

        ## ANIMATION PRINCIPLES

        1. The MOST IMPORTANT PRINCIPLE: The animation must be correct, coherent, and logical so
        that the user can learn the concept from the animation. Assume the user is a student
        learning the concept for the first time, and you are creating an animation to teach it to
        them for the very first time
        2. Every visual element must have a clear purpose in demonstrating the concept
        2. All related elements must animate together in a synchronized way, so organize them in
        groups in a logical order and design the animation so that groups animate together in a
        logical sequence
        3. Core concept elements should animate first, decorative elements (if any) only after the
        main concept is clear
        4. Use consistent timing and easing functions within related animations
        5. Animation sequence should follow a logical teaching progression
        6. Be careful not to accidentally leave components you intended to animate un-animated
        7. Unless otherwise specified or required, use a white background for the animation
        container
        
        ## SUPPORTED ANIMATION TECHNIQUES

        1. CSS Animations and Transitions:
           - Use @keyframes for complex animations with multiple steps
           - Use transitions for simple state changes
           - Always specify explicit durations in seconds (e.g., '0.5s', '2s')
           - Always set animation-iteration-count: 1
           - Prefer transform and opacity for smooth animations
           - Avoid animating layout properties (width, height, margin, etc.)
        2. JavaScript Animation Control:
           - Use setTimeout for sequencing animation steps
           - Use explicit numeric constants for timing (e.g., const stepDelay = 1000)
           - Combine related timeouts into a single constant (e.g., const totalDelay = baseDelay +
           stepDelay)
           - For forEach loops with setTimeout, use clear delay calculations (e.g., const
           totalDelay = initialPause + stepDelay * (idx + 1))
           - Avoid setInterval (use setTimeout for each step instead)
           - Avoid requestAnimationFrame (use CSS animations instead)
           - Keep all timing logic in one place for clarity
           - CRITICAL: When using forEach with setTimeout, ensure the delay calculation is on a
           separate line as a const variable
           - PREFERRED: Use simple sequential setTimeout calls instead of forEach loops when
           possible
           - If using forEach with timing, use patterns like: const totalDelay = baseDelay +
           stepDelay * idx
        3. State Changes:
           - Use CSS classes to trigger animations (e.g., .active, .visible, .complete)
           - Add/remove classes using JavaScript for state transitions
           - Use transitions for class-based state changes
           - Keep state management simple and linear
        4. Animation Coordination:
           - Group related animations using shared timing constants
           - Use consistent delay patterns for sequential steps
           - Calculate cumulative delays explicitly
           - Document timing relationships in comments
        5. Avoid:
           - Web Animation API (element.animate())
           - CSS animation-play-state manipulation
           - Dynamic duration calculations
           - Nested animation triggers
           - Event-based animation timing
           - Conditional animation paths
        
        ## ANIMATION APPROACH CONSTRAINTS

        To ensure reliable processing and conversion, follow these strict constraints:
        1. **PREFERRED: CSS-Only Animations**
           - For simple sequential reveals, use CSS transitions with opacity/transform
           - Trigger via class addition: element.classList.add('visible')
           - Use consistent timing: transition: opacity 0.5s ease, transform 0.5s ease
        2. **WHEN JAVASCRIPT IS NEEDED**
           - ONLY use setTimeout for sequencing (never setInterval, requestAnimationFrame, or Web
           Animation API)
           - ALWAYS use the pattern: setTimeout(() => { element.classList.add('class') }, delay)
           - NEVER manipulate CSS properties directly via JavaScript (use classes instead)
           - NEVER create complex timing loops or conditional animations
        3. **BANNED APPROACHES**
           - Dynamic DOM creation during animation (create all elements in HTML, show/hide with CSS)
           - Complex JavaScript timing calculations (keep delays simple: const delay = baseDelay +
           step * index)
           - Event listeners for animation sequencing (use timeouts only)
           - Recursive or nested setTimeout calls
           - Any timing that depends on user interaction or external events
           - Canvas, WebGL, or other dynamic rendering
        4. **SIMPLIFIED TIMING PATTERN**
           - Use this exact pattern for multi-step animations:
             ```javascript
             const initialDelay = 500;
             const stepDelay = 1000;
             
             setTimeout(() => { element1.classList.add('visible'); }, initialDelay);
             setTimeout(() => { element2.classList.add('visible'); }, initialDelay + stepDelay);
             setTimeout(() => { element3.classList.add('visible'); }, initialDelay + stepDelay * 2);
             ```
           - If you must use forEach, use this pattern:
             ```javascript
             const initialDelay = 500;
             const stepDelay = 1000;
             
             elements.forEach((element, idx) => {
                 const totalDelay = initialDelay + stepDelay * idx;
                 setTimeout(() => { element.classList.add('visible'); }, totalDelay);
             });
             ```
        5. **CONTENT CREATION CONSTRAINTS**
           - Create ALL visual elements in the HTML (no JavaScript DOM creation)
           - Use CSS for ALL visual styling and positioning
           - Use JavaScript ONLY for timing and class manipulation
           - Keep animations linear and predictable (no branching or conditional paths)
        
        ## ANIMATION TIMING AND PLAYBACK

        1. CRITICAL: All animations must play exactly once
           - Set animation-iteration-count: 1 for all CSS animations
           - Never use animation-iteration-count: infinite or numbers > 1
           - For CSS transitions, trigger them only once
           - For JavaScript animations, do not loop or repeat them
        2. Start the animation promptly, but after a short delay to allow the user to orient
           themselves to the animation
        3. Keep total duration to an appropriate length for the animation to illustrate the concept
           effectively, but not too long
        4. Use consistent animation appearance, animation, and disappearance timing for related
           elements
        5. Add sizable (but not excessive) delays between sequential steps that enable a person
           learning the concept to understand each step. Delays of 3-5 seconds are often
           appropriate, but may be shorter for minor animation updates or longer for major animation
           updates
        6. Choose whether elements should appear or enter the frame based on what makes the most
           sense for the concept being illustrated
        7. For elements entering frame, start from far enough outside the container that none of
           the element is visible before the animation starts, but within overflow
        8. Use the same animation timing and style for objects and their labels so they are clearly
           related
        
        ## TEXT PLACEMENT AND READABILITY
        1. Rules for all text:
           - Do not use special characters to represent fractions. Use the / symbol instead
           - Consider using a semi-transparent background for text to make it more readable
           - Consider using a contrasting color for text to make it more readable
        2. Instructional Text:
           - CRITICAL: Position over non-essential areas of the animation. Instructional text must
           not overlap key elements of the animation (points, lines, shapes, etc.), or any other
           text.
           - Use a semi-transparent background (e.g., background: rgba(255,255,255,0.8))
           - Reserve top 120px for titles and step descriptions
           - Place longer explanations in bottom third of container
           - Test text placement at all animation stages
           - If you want to place sequential instructions in the same location, ensure earlier text
           animates away before later text animates in so that the instructions don't overlap
        3. Labels and Annotations:
           - Can overlay mathematical elements (points, lines, shapes), but NOT other text elements
           - Use contrasting colors with sufficient contrast ratio
           - Position to minimize overlap with other labels
           - For point coordinates: offset slightly from point
           - For line labels: place parallel to line
           - For shape labels: on top of the center of the shape
           - Consider adding subtle text shadows for contrast
           - Be careful not to rotate labels unintentionally, such as when rotating a shape+label
           element to place it in a certain direction. When doing this, make sure to rotate the
           label to compensate
        4. Text Hierarchy:
           - Title: largest, centered at top
           - Step descriptions: medium, below title
           - Labels: smallest, near relevant elements, with a higher z-coordinate than non-text
           elements
           - Use consistent fonts and sizes throughout
           - Remember that depending on text size and container size, longer text may wrap to
           multiple lines, so be careful to account for line breaks when placing text
               - You can widen the container as high as 950px to reduce line breaks
               - You can reduce font sizes to reduce line breaks, but be careful not to make the
               text too small for its role in the animation
               - For example, a long title may wrap to multiple lines, so it may overlap a substitle
               if you don't account for line breaks
        
        ## MATHEMATICAL PRECISION

        CRITICAL - Coordinate Systems: We work with two coordinate systems.
        1. Mathematical (Cartesian): y increases upward
        2. CSS: y increases downward
        When determining the position of Cartesian elements in the CSS animation, make sure to
        subtract CSS coordinates when the Cartesian y-coordinate increases, and add CSS coordinates
        when the Cartesian y-coordinate decreases. For example, if you are illustrating "rise over
        run" in a line graph, a POSITIVE rise in the Cartesian coordinate system corresponds to a
        NEGATIVE change in the CSS coordinate system.
        
        When creating mathematically precise animations (graphs, geometric shapes, etc.):
        1. Start by performing your mathematical reasoning:
           1. Define coordinate system:
              - Container dimensions: 1024x1024px with 10px padding
              - Usable area: 1004x1004px
              - Origin: (512, 512) at exact center of the animation container
           2. Calculate positions and sizes for critical elements:
              - Reason about the position and size of ALL critical elements in the logical
              coordinate system you are using.
                  - You MUST place elements whose precise position and size is critical to a user
                  learning about the concept from the animation so that they are correctly
                  positioned relative to each other and the origin, axes, grid lines, etc.
                  - Pay close attention to the position and angle of any lines or curves in the
                  animation, especially if they are supposed to touch or pass through important
                  points. Reason about the position and angle of the lines or curves in the
                  Cartesian coordinate system, and then convert them to CSS coordinates so they are
                  correctly positioned in the animation.
                  - Ensure the positions and sizes of elements which have some sort of relationship
                  to each other are correct and consistent with each other. For example, if you are
                  animating wedges appearing in a circle outline, the position of the wedges should
                  overlap the appropriate position in the circle outline, and the radius of the
                  circle should be consistent with the radius of the wedges.
              - Convert the position and size of the element in the logical coordinate system to CSS
              coordinates, following the same rules and reasoning used for defining the coordinate
              system
              - Cross-check your calculations for critical elements with multiple points/elements
              within the animation, such as the origin, axes, and grid lines
              - Ensure you place fills within the portion of an object you wish to fill. For
              example, when creating a circle sector to illustrate a wedge, the fill should be
              placed within the sector, not outside of it.
              - If necessary, revise your calculations until you are confident in the positions of
              critical elements
           3. Verify calculations:
              - Test multiple points/elements within the animation
              - Confirm distances match scale
              - Check angles match math
              - Ensure transformations preserve proportions
        2. Grid and Axes Requirements:
           - Axes are the x=0 and y=0 lines, with both axes passing directly through the origin
           - Do not draw grid lines for x=0 and y=0. Use the axes as the grid lines for x=0 and y=0.
           DO NOT create separate grid lines for x=0 and y=0
           - Other grid line positions should be calculated by translating their mathematical
             coordinates in the coordinate system to CSS coordinates, working outward from the axes.
             YOU MUST ALWAYS position grid lines relative to the axes, or else the user will not be
             able to understand the animation.
           - Grid lines should be drawn in the same color as the axes
           - Axes must be thicker than grid lines
           - CRITICAL VISIBILITY: Use high-contrast colors for mathematical elements:
             * Axes: #000000 (black) or #333333 (dark gray), minimum 3px thick
             * Grid lines: #666666 or #888888 (medium gray), NOT light colors like #ccc
             * Points: bright colors like #FF0000 (red), #0066CC (blue), #00AA00 (green), 12-16px
             diameter
             * Lines: bright colors with 3-4px thickness minimum
           - Include coordinate labels at key grid intersections showing numeric values
        3. Element Positioning:
           - Reason about elements using the coordinate system, but when placing them in the CSS,
           explicitly
           calculate the CSS coordinates from the mathematical coordinate system
           - Reason about element positions in the coordinate system (with particular attention to
           their position relative to other important components like axes or grid lines), but when
           placing them in the CSS, explicitly calculate the CSS coordinates from the mathematical
           coordinate system
           - Record all calculations in your reasoning
           - MATHEMATICAL ACCURACY: For functions like y = mx + b, establish a clear scale (e.g.,
             50px = 1 unit) and verify that all points actually satisfy the equation. Convert
             coordinates using: cssX = 512 + (x_value × scale), cssY = 512 - (y_value × scale)
        
        ## TECHNICAL REQUIREMENTS

        1. The animation container must be exactly 1024x1024px with 10px padding and white
        background:
           .animation-container {
               width: 1024px;
               height: 1024px;
               padding: 10px;
               box-sizing: border-box;
               background: white;
           }
        2. All elements must remain fully within the animation container at all times
        3. Animation must play exactly once (animation-iteration-count: 1)
        4. Use CSS transforms for animations instead of position/size changes
        5. Center elements using transform: translate(-50%, -50%) with position: absolute
        6. All measurements must use px units
        7. Add aria-label to the container describing the animation
        
        ## POSITIONING AND LAYOUT
        
        1. Use position: relative on container and position: absolute on elements
        2. Calculate exact positions to ensure perfect alignment
        3. When elements need to align (like shapes touching), use precise calculations
        4. For circular/curved elements, ensure border-radius matches dimensions
        5. Account for border widths in size calculations
        6. Use transform-origin appropriately for rotations
        
        ## CODE QUALITY

        1. Group CSS by component with clear comments
        2. Use semantic class names
        3. Include ARIA attributes for accessibility
        4. Add helpful comments for complex calculations
        5. Organize keyframes at the end of CSS
        6. Do not include anything in the HTML file besides the final animation code"""

        user_prompt = f"""Create an educational animation that demonstrates: {prompt}

        First, perform your mathematical reasoning and calculations. Then create the animation
        following that reasoning.
        
        Remember to test your calculations with multiple points to verify accuracy. Do not loop the
        animation. Play it a single time only, even if you have other instructions to loop the
        animation."""

        client = get_async_openai_client(timeout=300.0)
        response = await client.chat.completions.create(
            model="o3",
            messages=[
                {"role": "developer", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )

        if response.choices[0].finish_reason != 'stop':
            raise Exception(f"Failed to generate animation: {response.choices[0].finish_reason}")

        # Defensive check: ensure content is not a coroutine
        response_content = response.choices[0].message.content
        if hasattr(response_content, '__await__'):
            response_content = await response_content
        html_code = _clean_html_code(response_content)
        logger.info(f"HTML code: {html_code}")
        logger.info("Successfully generated animation code")
        return html_code

    except Exception as e:
        logger.error(f"Error generating animation: {e}")
        raise

async def generate_animation(prompt: str, max_retries: int = 3) -> str:
    """
    Generate an educational HTML animation and convert it to an animated GIF.
    
    Parameters
    ----------
    prompt : str
        Description of the animation to generate
    max_retries : int, default 3
        Maximum number of retry attempts
        
    Returns
    -------
    str
        JSON string containing the URL of the generated GIF
    """
    logger.info(f"Generating animation with prompt (attempts remaining: {max_retries}): {prompt}")
    
    try:
        # Generate HTML animation
        html_code = await _generate_animation_html(prompt)
        
        # Capture frames and get duration
        frames, duration, fps = _capture_animation_frames(html_code)
        
        # Convert to GIF
        gif_bytes = _create_gif_from_frames(frames, duration, fps)
        
        # Upload to Supabase
        gif_url = upload_image_to_supabase(
            image_bytes=gif_bytes,
            content_type="image/gif",
            bucket_name="incept-images",
            file_extension=".gif"
        )
        
        result = {
            "animation_url": gif_url,
            "status": "success"
        }
        
        return json.dumps(result)
        
    except Exception as e:
        if max_retries > 0:
            logger.error(f"Failed to generate animation: {e}")
            return await generate_animation(prompt, max_retries - 1)
        else:
            logger.error(f"Failed to generate animation: {e}")
            return json.dumps({
                "animation_url": None,
                "status": "failed",
                "error": str(e)
            })

def generate_animation_tool() -> tuple[dict, Callable]:
    spec = {
        "type": "function",
        "name": "generate_animation",
        "description": "Generate an educational HTML animation and convert it to an animated GIF. "
                       "Returns a JSON string containing the URL of the generated animation.",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Description of the educational animation to generate, such as "
                                   "mathematical concepts, scientific processes, or other "
                                   "educational demonstrations."
                }
            },
            "required": ["prompt"]
        }
    }
    return spec, generate_animation 