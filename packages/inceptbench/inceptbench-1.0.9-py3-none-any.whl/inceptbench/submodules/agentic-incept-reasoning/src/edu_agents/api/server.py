from __future__ import annotations

import asyncio
import json
import logging
import multiprocessing
import os
import time
import uuid
from datetime import datetime
from typing import Any, AsyncGenerator, AsyncIterable, Dict, Literal

import psutil
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from edu_agents import __version__ as API_VERSION
from edu_agents.core.api_key_manager import get_api_key_manager
from edu_agents.core.basic_agent import BasicAgent
from edu_agents.eval import comprehensive_evaluate
from edu_agents.eval.simple_content_qc import get_qc_stats
from edu_agents.generator import GeneratorAgent
from edu_agents.tools.athena_formatter import (
    UnknownContentTypeError,
    UnsupportedContentTypeError,
    generate_athena_formatter_tool,
)
from edu_agents.tools.qti_generator import generate_qti_tool

# Import OpenAI errors for better error handling
try:
    import socket

    import requests
    from httpx import ConnectTimeout, ReadTimeout, TimeoutException, WriteTimeout
    from openai import APIConnectionError, APIError, APITimeoutError, RateLimitError
except ImportError:
    # Fallback if OpenAI package structure changes
    APIError = Exception
    RateLimitError = Exception
    APIConnectionError = Exception
    APITimeoutError = Exception
    TimeoutException = Exception
    ReadTimeout = Exception
    WriteTimeout = Exception
    ConnectTimeout = Exception
    socket = None
    requests = None

from utils.supabase_utils import (
    create_request_log,
    find_request_by_content,
    find_successful_retry_record,
    get_location_from_ip,
    get_request_log,
    update_request_log_evaluation,
    update_request_log_feedback,
    update_request_log_response,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress httpx HTTP request logs to reduce clutter
logging.getLogger("httpx").setLevel(logging.WARNING)

# Log the API version on startup
logger.info(f"Educational Content Generator API v{API_VERSION} starting up")

# Phase 2: Pure async architecture - no thread pools needed
# All agent execution now uses asyncio.create_task() for concurrent async tasks
cpu_count = multiprocessing.cpu_count()
logger.info(f"Running on {cpu_count} vCPUs with pure async architecture (no thread pools)")

def get_client_ip(request: Request) -> str:
    """
    Extract the client IP address from the request, handling proxies and load balancers.
    """
    # Check for common proxy headers first
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # X-Forwarded-For can contain multiple IPs, take the first one (original client)
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
    # Fallback to direct client IP
    return request.client.host if request.client else "unknown"

async def get_client_info(request: Request) -> Dict[str, Any]:
    """
    Extract client information from the request including IP, user agent, and location.
    """
    client_ip = get_client_ip(request)
    user_agent = request.headers.get("User-Agent", "")
    
    # Get location data (this might take a moment, so we do it async)
    location_data = None
    if client_ip and client_ip != "unknown":
        try:
            location_data = await get_location_from_ip(client_ip)
        except Exception as e:
            logger.warning(f"Failed to get location for IP {client_ip}: {str(e)}")
    
    return {
        "client_ip": client_ip,
        "user_agent": user_agent,
        "location_data": location_data
    }

def create_json_response(content: dict, status_code: int = 200) -> JSONResponse:
    """
    Helper function to create standardized JSON responses with API version.
    """
    if isinstance(content, dict):
        # Add api_version to the content if it's not already there
        if "api_version" not in content:
            content["api_version"] = API_VERSION
    
    return JSONResponse(content=content, status_code=status_code)

app = FastAPI(
    title="Educational Content Generator API",
    version=API_VERSION,
    description="API for generating and evaluating educational content"
)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Serve favicon.ico specifically at the root
favicon_path = os.path.join(static_dir, "favicon.ico")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path, media_type="image/x-icon")
    else:
        return create_json_response(content={"error": "Favicon not found"}, status_code=404)

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    global shutdown_flag
    logger.info("Shutting down application")
    
    # Set shutdown flag for graceful shutdown
    shutdown_flag = True
    
    # Note: Chrome/browser management is now handled by the Node.js screenshot service
    # No explicit cleanup needed here - screenshot service manages its own browsers
    
    # Phase 2: No thread pool to shutdown - using pure async tasks
    # Async tasks will be cancelled automatically by FastAPI on shutdown
    
    logger.info("Application shutdown completed")

# Global shutdown flag
shutdown_flag = False

def format_sse_event(event_data: Dict[str, Any]) -> str:
    """
    Format an event as a proper SSE (Server-Sent Events) message.
    
    According to SSE specification, each event should be formatted as:
    data: {json_content}
    
    (terminated by double newline)
    
    Args:
        event_data: Dictionary containing the event data
        
    Returns:
        Properly formatted SSE event string
    """
    json_str = json.dumps(event_data)
    return f"data: {json_str}\n\n"

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info(f"Educational Content Generator API v{API_VERSION} starting up...")
    
    # Note: Browser pool configuration is now handled by the Node.js screenshot service
    # Configuration is set via environment variables (MAX_BROWSERS, MAX_PAGES_PER_BROWSER)

# Add graceful shutdown middleware
@app.middleware("http")
async def graceful_shutdown_middleware(request: Request, call_next):
    """Middleware to handle graceful shutdown."""
    global shutdown_flag
    
    # Always allow health checks
    if request.url.path == "/health":
        return await call_next(request)
    
    # Reject new non-health requests if shutting down
    if shutdown_flag:
        return create_json_response(
            content={"error": "Service is shutting down, please try again shortly"},
            status_code=503
        )
    
    return await call_next(request)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RequestLogger:
    """Handles logging of requests to the database."""
    
    def __init__(self, request_id: str, prompt: str, model: str,
    client_info: Dict[str, Any] = None):
        self.request_id = request_id
        self.prompt = prompt
        self.model = model
        self.api_version = API_VERSION
        self.client_info = client_info or {}
        self.reasoning_parts = []
        self.final_response = ""
        self.error_message = None
        self.error_type = None
        self.start_time = time.time()  # Store start time in seconds
        self.response_time = None
        self.is_error = False
        
    async def create_initial_log(self, conversation_id: str = None) -> None:
        """Create the initial log entry in the database."""
        try:
            await create_request_log(
                self.request_id, 
                self.prompt, 
                self.model, 
                self.api_version,
                client_ip=self.client_info.get("client_ip"),
                user_agent=self.client_info.get("user_agent"),
                location_data=self.client_info.get("location_data")
            )
        except Exception as e:
            logger.error(f"Failed to create initial log for {self.request_id}: {str(e)}")
    
    def add_reasoning_delta(self, delta: str) -> None:
        """Add a reasoning delta to the accumulated reasoning."""
        if isinstance(delta, dict) and "text" in delta:
            self.reasoning_parts.append(delta["text"])
        elif isinstance(delta, str):
            self.reasoning_parts.append(delta)
    
    def set_final_response(self, response: str | dict) -> None:
        """Set the final response and calculate response time."""
        if isinstance(response, dict) and "text" in response:
            self.final_response = response["text"]
        elif isinstance(response, str):
            self.final_response = response
        else:
            self.final_response = str(response)
        
        # Calculate response time when final response is set
        end_time = time.time()
        self.response_time = round(end_time - self.start_time, 3)
        self.is_error = False
    
    def set_error(self, error_message: str, error_type: str) -> None:
        """Set error information and calculate response time."""
        self.error_message = error_message
        self.error_type = error_type
        self.is_error = True
        
        # Calculate response time when error is set
        end_time = time.time()
        self.response_time = round(end_time - self.start_time, 3)
    
    async def finalize_log(self) -> None:
        """Update the log with final response or error information."""
        try:
            reasoning_text = "".join(self.reasoning_parts)
            
            if self.is_error:
                # Log error information - don't set it as a final response
                # The error information can be stored in a separate field or as a special marker
                error_response = f"[ERROR] {self.error_type}: {self.error_message}"
                await update_request_log_response(
                    self.request_id, 
                    error_response,  # Store error with clear marking
                    reasoning_text,
                    self.response_time
                )
            else:
                # Log successful response normally
                await update_request_log_response(
                    self.request_id, 
                    self.final_response, 
                    reasoning_text,
                    self.response_time
                )
        except Exception as e:
            logger.error(f"Failed to finalize log for {self.request_id}: {str(e)}")

class EventStreamResponse(StreamingResponse):
    """Custom StreamingResponse that logs when events are actually sent."""
    
    def __init__(self, content: AsyncIterable[str], request_id: str, **kwargs):
        self.request_id = request_id
        super().__init__(self._log_events(content), **kwargs)
    
    async def _log_events(self, content: AsyncIterable[str]) -> AsyncGenerator[str, None]:
        async for event in content:
            yield event

async def heartbeat_task(event_queue: asyncio.Queue, request_id: str, 
                        heartbeat_interval: float = 30.0):
    """
    Background task that sends periodic heartbeat events to keep the connection alive.
    This prevents network timeouts (NAT gateways, load balancers, firewalls, etc.) from 
    closing idle connections during long-running operations like QC checks or API calls.
    
    Heartbeats are sent every 30 seconds by default, which is well within typical 
    60-second idle connection timeouts. Clients can safely ignore heartbeat events.
    
    Args:
        event_queue: Queue to send heartbeat events to
        request_id: Request ID for the heartbeat events
        heartbeat_interval: Seconds between heartbeat events (default 30s)
    """
    try:
        heartbeat_count = 0
        while True:
            await asyncio.sleep(heartbeat_interval)
            heartbeat_count += 1
            
            heartbeat_event = {
                "type": "heartbeat",
                "data": {
                    "sequence": heartbeat_count,
                    "timestamp": datetime.utcnow().isoformat()
                },
                "request_id": request_id,
                "api_version": API_VERSION
            }
            
            try:
                event_queue.put_nowait(format_sse_event(heartbeat_event))
                logger.debug(f"Request {request_id} sent heartbeat #{heartbeat_count}")
            except asyncio.QueueFull:
                # Queue full, skip this heartbeat (very unlikely)
                logger.warning(
                    f"Request {request_id} queue full, skipped heartbeat #{heartbeat_count}"
                )
                
    except asyncio.CancelledError:
        # Normal cancellation when request completes
        logger.debug(f"Request {request_id} heartbeat task cancelled after {heartbeat_count} beats")
        raise

async def event_generator(prompt: str, request_id: str, conversation_id: str, user_id: str,
model: Literal["incept", "o3"] = "incept", client_info: Dict[str, Any] = None,
timeout_seconds: float = 600, amq_json_format: bool = True, include_reasoning: bool = False,
use_coach_bot_tools: bool = False) -> AsyncGenerator[str, None]:
    """
    Generates Server-Sent Events from the GeneratorAgent's or BasicAgent's output.
    Each event is formatted according to SSE standards with "data: " prefix and double newlines.
    The JSON payload contains:
    - type: the event type (text_delta, reasoning_delta, echo_result, tool_final, response_final)
    - data: the event payload
    - request_id: the unique request identifier
    - api_version: the API version
    
    Args:
        include_reasoning: If False, reasoning_delta events are not streamed but still 
                         collected for logging
    
    All conversations use ZDR-compatible conversation management.
    
    Phase 2: Pure async implementation - no threads, no executors, just async tasks.
    """
    logger.info(f"Starting request {request_id} using model: {model} with prompt: {prompt}")
    
    # Create request logger (initial log will be created after we determine conversation_id)
    request_logger = RequestLogger(request_id, prompt, model, client_info)
    
    # Phase 2: Use async queue and async task cancellation
    event_queue: asyncio.Queue = asyncio.Queue()
    agent_task: asyncio.Task = None  # Will hold the async agent execution task
    
    def queue_event(event_type: str, data: Any) -> None:
        """Callback for the agent to queue events (synchronous callback for async queue)"""
        # Always log reasoning deltas to our request logger for database storage
        if event_type == "reasoning_delta":
            request_logger.add_reasoning_delta(data)
            # Skip streaming reasoning_delta events if include_reasoning is False
            if not include_reasoning:
                return
        elif event_type == "response_final":
            # Check if this is actually a "give up" message from the generator agent
            response_text = ""
            if isinstance(data, dict) and "text" in data:
                response_text = data["text"]
            elif isinstance(data, str):
                response_text = data
            
            if ("Unable to generate content of sufficient quality after multiple attempts" 
                    in response_text):
                # Convert this to an error event instead of response_final
                logger.warning(f"Request {request_id} generator gave up after QC attempts")
                event_type = "error"
                data = {
                    "text": response_text,
                    "error_type": "QualityCheckFailed"
                }
                request_logger.set_error(response_text, "QualityCheckFailed")
            else:
                # Normal response_final handling
                request_logger.set_final_response(data)
                data_length = len(str(data)) if data else 0
                logger.info(f"Request {request_id} agent emitted response_final event " +
                            f"(data length: {data_length})")
        
        event = {
            "type": event_type,
            "data": data,
            "request_id": request_id,
            "api_version": API_VERSION
        }
        # Queue the SSE-formatted event (use put_nowait for asyncio.Queue from sync callback)
        try:
            event_sse = format_sse_event(event)
            event_queue.put_nowait(event_sse)
            if event_type == "response_final":
                logger.info(f"Request {request_id} response_final event successfully " +
                           "queued for streaming")
            elif event_type in ["error", "retry_attempt"]:
                logger.info(f"Request {request_id} {event_type} event queued")
        except Exception as e:
            logger.error(f"Request {request_id} failed to queue {event_type} event: {str(e)}")
            raise
    
    # Phase 2: Create and run the agent as an async task
    async def run_agent():
        max_retries = 2
        retry_count = 0
        start_time = time.time()
        
        while retry_count <= max_retries:
            # Phase 2: No cancellation flag checks - asyncio.CancelledError will be raised
            # when the task is cancelled, providing natural cancellation flow
            
            # Generate a new request ID for retry attempts
            current_request_id = (request_id if retry_count == 0 
                                 else f"{request_id}_retry_{retry_count}")
            
            # Update the request logger to use the current request ID for this attempt
            if retry_count > 0:
                request_logger.request_id = current_request_id
                # Reset timing for the retry attempt
                request_logger.start_time = time.time()
                
            # Check if we've exceeded the total timeout
            elapsed_time = time.time() - start_time
            if elapsed_time >= timeout_seconds:
                timeout_event = {
                    "type": "error",
                    "data": {
                        "text": f"Request exceeded maximum timeout of {timeout_seconds} seconds. "
                                "Please try again with a simpler prompt or increase the timeout.",
                        "error_type": "RequestTimeout"
                    },
                    "request_id": request_id,  # Use original request_id for client consistency
                    "api_version": API_VERSION
                }
                event_queue.put_nowait(format_sse_event(timeout_event))
                request_logger.set_error(f"Exceeded {timeout_seconds}s timeout", "RequestTimeout")
                break
            
            try:
                # Phase 2: Choose agent based on model parameter (no cancellation_flag needed)
                if model == "incept":
                    agent = GeneratorAgent(
                        on_event=queue_event, 
                        conversation_id=conversation_id,
                        user_id=user_id,
                        amq_json_format=amq_json_format,
                        request_id=current_request_id,  # Use current request ID for agent
                        use_coach_bot_tools=use_coach_bot_tools
                    )
                else:  # model == "o3"
                    agent = BasicAgent(
                        model="o3", 
                        on_event=queue_event, 
                        conversation_id=conversation_id,
                        user_id=user_id,
                        amq_json_format=amq_json_format,
                        request_id=current_request_id  # Use current request ID for agent
                    )
                    
                logger.info(
                    f"Request {current_request_id} created agent with conversation ID: "
                    f"{agent.conv.conversation_id}"
                )
                
                # Phase 2: Direct await (no asyncio.run wrapper needed)
                await request_logger.create_initial_log(agent.conv.conversation_id)
                
                logger.info(
                    f"Request {current_request_id} starting agent execution (attempt "
                    f"{retry_count + 1}/{max_retries + 1})"
                )
                
                # Phase 2: Direct await for async agent execution
                await agent.run_async(prompt)
                    
                logger.info(f"Request {current_request_id} agent execution completed successfully")
                break  # Success, exit retry loop
            
            except RuntimeError as e:
                # Handle QC failures specifically
                if "Content failed quality check" in str(e):
                    logger.warning(f"QC failure for request {current_request_id}: {str(e)}")
                    qc_error_event = {
                        "type": "error",
                        "data": {
                            "text": "Unable to generate content of sufficient quality.",
                            "error_type": "QualityCheckFailed"
                        },
                        "request_id": request_id,  # Use original request_id for client consistency
                        "api_version": API_VERSION
                    }
                    event_queue.put_nowait(format_sse_event(qc_error_event))
                    request_logger.set_error("Content failed quality check", "QualityCheckFailed")
                    break  # Don't retry QC failures
                else:
                    # Re-raise other RuntimeErrors
                    raise
                
            except (APITimeoutError, TimeoutException, ReadTimeout, WriteTimeout, ConnectTimeout, 
                    socket.timeout if socket else type(None), 
                    requests.exceptions.Timeout if requests else type(None),
                    requests.exceptions.ConnectionError if requests else type(None)) as e:
                retry_count += 1
                error_msg = (f"Timeout error in agent execution for request {current_request_id} " +
                            f"(attempt {retry_count}/{max_retries + 1}): {type(e).__name__}: " +
                            f"{str(e)}")
                logger.warning(error_msg)
                
                if retry_count <= max_retries:
                    # Send a retry notification to the client
                    retry_event = {
                        "type": "retry_attempt",
                        "data": {
                            "text": f"Request timed out, retrying... (attempt {retry_count + 1})",
                            "attempt": retry_count + 1,
                            "max_attempts": max_retries + 1
                        },
                        "request_id": request_id,  # Use original request_id for client consistency
                        "api_version": API_VERSION
                    }
                    event_queue.put_nowait(format_sse_event(retry_event))
                    
                    # Phase 2: Simple async sleep - task cancellation will interrupt naturally
                    backoff_time = min(2 ** retry_count, 10)
                    logger.info(
                        f"Request {request_id} waiting {backoff_time}s before retry "
                        f"{retry_count + 1}"
                    )
                    await asyncio.sleep(backoff_time)
                    continue
                else:
                    # Final timeout error after all retries
                    user_message = "The request timed out after multiple attempts. This may be " + \
                                   "due to high demand or a complex prompt. Please try again " + \
                                   "with a simpler request or try again later."
                    error_type = "TimeoutError"
                    
                    error_event = {
                        "type": "error",
                        "data": {
                            "text": user_message,
                            "error_type": error_type
                        },
                        "request_id": request_id,  # Use original request_id for client consistency
                        "api_version": API_VERSION
                    }
                    event_queue.put_nowait(format_sse_event(error_event))
                    request_logger.set_error(str(e), error_type)
                    break
                    
            except APIError as e:
                # Handle OpenAI API errors - retry if it seems like a transient error
                error_str = str(e).lower()
                is_retryable_api_error = any(phrase in error_str for phrase in [
                    'error occurred while processing the request',
                    'internal server error',
                    'service unavailable',
                    'temporarily unavailable',
                    'please try again'
                ])
                
                # Special logging for the specific error we're tracking
                if 'error occurred while processing the request' in error_str:
                    logger.warning(
                        f"Request {current_request_id} encountered the generic OpenAI processing "
                        "error - this should now be retried"
                    )
                
                if is_retryable_api_error and retry_count < max_retries:
                    retry_count += 1
                    logger.warning(
                        f"Retryable API error in agent execution for request {current_request_id} "
                        f"(attempt {retry_count}/{max_retries + 1}): {type(e).__name__}: {str(e)}"
                    )
                    
                    # Send a retry notification to the client
                    retry_event = {
                        "type": "retry_attempt",
                        "data": {
                            "text": "AI service encountered an error, retrying... " + \
                                    f"(attempt {retry_count + 1})",
                            "attempt": retry_count + 1,
                            "max_attempts": max_retries + 1
                        },
                        "request_id": request_id,  # Use original request_id for client consistency
                        "api_version": API_VERSION
                    }
                    event_queue.put_nowait(format_sse_event(retry_event))
                    
                    # Phase 2: Simple async sleep - task cancellation will interrupt naturally
                    backoff_time = min(2 ** retry_count, 10)
                    logger.info(
                        f"Request {request_id} waiting {backoff_time}s before retry "
                        f"{retry_count + 1}"
                    )
                    await asyncio.sleep(backoff_time)
                    continue
                else:
                    # Non-retryable API error or max retries exceeded
                    if is_retryable_api_error:
                        logger.error(
                            f"API error in agent execution for request {current_request_id} - "
                            f"max retries exceeded: {type(e).__name__}: {str(e)}"
                        )
                        user_message = "The AI service encountered repeated errors. Please try " + \
                                       "again in a few moments."
                        error_type = "RepeatedAPIError"
                    else:
                        logger.error(
                            f"Non-retryable API error in agent execution for request "
                            f"{current_request_id}: {type(e).__name__}: {str(e)}"
                        )
                        user_message = "The AI service encountered an error processing your " + \
                                       "request. Please try again or rephrase your prompt."
                        error_type = "APIError"
                    
                    # Send an error event to the client
                    error_event = {
                        "type": "error",
                        "data": {
                            "text": user_message,
                            "error_type": error_type
                        },
                        "request_id": request_id,  # Use original request_id for client consistency
                        "api_version": API_VERSION
                    }
                    event_queue.put_nowait(format_sse_event(error_event))
                    request_logger.set_error(str(e), error_type)
                    break
                
            except Exception as e:
                # Handle any other errors during agent execution
                import traceback
                full_traceback = traceback.format_exc()
                logger.error(
                    f"Non-timeout error in agent execution for request {current_request_id}: "
                    f"{type(e).__name__}: {str(e)}"
                )
                logger.error(f"Full traceback for request {current_request_id}:\n{full_traceback}")
                
                # Check if this might be a timeout-related error we didn't catch
                error_str = str(e).lower()
                if any(timeout_keyword in error_str for timeout_keyword \
                    in ['timeout', 'timed out', 'read timeout', 'connection timeout']):
                    logger.warning(
                        f"Request {current_request_id} appears to be a timeout error but "
                        f"wasn't caught by timeout handlers: {type(e).__name__}: {str(e)}"
                    )
                    
                    # Treat as timeout and retry if we haven't exceeded max retries
                    if retry_count < max_retries:
                        retry_count += 1
                        logger.info(
                            f"Request {current_request_id} treating as timeout, attempting retry "
                            f"{retry_count + 1}/{max_retries + 1}"
                        )
                        
                        retry_event = {
                            "type": "retry_attempt",
                            "data": {
                                "text": ("Request encountered an error, retrying... (attempt " +
                                        f"{retry_count + 1})"),
                                "attempt": retry_count + 1,
                                "max_attempts": max_retries + 1
                            },
                            "request_id": request_id,
                            "api_version": API_VERSION
                        }
                        event_queue.put_nowait(format_sse_event(retry_event))
                        
                        # Phase 2: Simple async sleep - task cancellation will interrupt naturally
                        backoff_time = min(2 ** retry_count, 10)
                        logger.info(
                            f"Request {request_id} waiting {backoff_time}s before retry "
                            f"{retry_count + 1}"
                        )
                        await asyncio.sleep(backoff_time)
                        continue
                
                # Determine user-friendly error message based on error type
                if isinstance(e, RateLimitError):
                    user_message = "The service is currently experiencing high demand. Please " + \
                                   "try again in a few moments."
                    error_type = "RateLimitError"
                elif isinstance(e, APIConnectionError):
                    user_message = "Unable to connect to the AI service. Please check your " + \
                                   "connection and try again."
                    error_type = "ConnectionError"
                else:
                    user_message = f"An unexpected error occurred: {str(e)}"
                    error_type = type(e).__name__
                
                # Send an error event to the client
                error_event = {
                    "type": "error",
                    "data": {
                        "text": user_message,
                        "error_type": error_type
                    },
                    "request_id": request_id,  # Use original request_id for client consistency
                    "api_version": API_VERSION
                }
                event_queue.put_nowait(format_sse_event(error_event))
                
                # Also set an error response for logging
                request_logger.set_error(str(e), error_type)
                break
                
        # Phase 2: Signal completion via queue
        logger.info(f"Request {request_id} agent task signaling completion")
        event_queue.put_nowait(None)
        logger.info(f"Request {request_id} agent task completed and signaled end")
    
    # Phase 2: Create async task instead of thread pool submission
    # Pre-flight resource check - monitor system resources
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    if swap.percent > 90:
        # System is thrashing, log warning but proceed (async is much more lightweight)
        logger.warning(f"Warning: {request_id} proceeding despite swap exhaustion: " + 
                    f"{swap.percent:.1f}%")
    
    # Phase 2: Create the agent task - no try/except needed, task creation won't fail
    logger.info(f"Request {request_id} creating async agent task")
    agent_task = asyncio.create_task(run_agent())
    logger.info(f"Request {request_id} agent task created successfully")
    
    # Start heartbeat task to prevent network idle timeouts
    # This sends periodic events even when no agent events are being generated
    # (e.g., during QC checks, LaTeX fixing, or long API calls)
    heartbeat = asyncio.create_task(
        heartbeat_task(event_queue, request_id, heartbeat_interval=30.0)
    )
    logger.info(f"Request {request_id} heartbeat task started (30s interval)")
    
    # Monitor system resources and log warnings for resource pressure
    if memory.percent > 85:
        logger.warning(f"High memory usage: {memory.percent:.1f}%")
    if swap.percent > 50:
        logger.error(f"Excessive swap usage: {swap.percent:.1f}% - " + 
                    "system under memory pressure")
    
    # Stream events from the queue with request logging context
    events_sent = 0
    final_event_sent = False
    error_event_sent = False  # Track if we sent an intentional error response
    
    try:
        # Log the start of event streaming
        logger.info(f"Request {request_id} starting SSE event streaming")
        
        while True:
            # Phase 2: Direct async queue get - no executor needed
            try:
                event = await event_queue.get()
            except Exception as e:
                logger.error(f"Request {request_id} failed to retrieve event from queue: {str(e)}")
                raise
                
            if event is None:  # End signal
                logger.info(
                    f"Request {request_id} received end signal from agent task, " +
                    f"ending stream (events_sent: {events_sent}, " +
                    f"final_sent: {final_event_sent}, error_sent: {error_event_sent})"
                )
                
                # CRITICAL: Perform database logging BEFORE sending stream_end
                # This ensures the database is updated even if the client disconnects
                # during the final event transmission
                try:
                    # Shield the database operation from cancellation
                    await asyncio.shield(request_logger.finalize_log())
                    logger.info(f"Request {request_id} database log finalized before stream end")
                except Exception as db_err:
                    logger.error(f"Request {request_id} failed to finalize database log: {db_err}")
                
                # Send explicit stream termination in consistent SSE format
                stream_end_event = {
                    "type": "stream_end",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": request_id
                }
                yield format_sse_event(stream_end_event)
                
                # CRITICAL: Give the event loop a chance to process pending I/O
                # before the generator exits. This ensures stream_end_event is fully
                # flushed to the client. Using a shorter delay since DB logging is done.
                try:
                    await asyncio.sleep(0.3)
                except asyncio.CancelledError:
                    # Client closed connection after receiving stream_end (expected behavior)
                    # This is actually a good sign - client got everything and closed cleanly
                    logger.debug(
                        f"Request {request_id} client closed connection after stream_end " +
                        "(expected clean shutdown)"
                    )
                    # Don't re-raise - this is normal, everything was already sent
                break
            
            # Track if we're sending the final response event
            event_type = None  # Initialize to avoid NameError
            event_data = None
            
            try:
                # Extract JSON from SSE format: "data: {json}\n\n"
                event_clean = event.rstrip('\n')
                if event_clean.startswith('data: '):
                    json_str = event_clean[6:]  # Remove "data: " prefix
                    if json_str.strip():  # Only parse if there's actual content
                        event_data = json.loads(json_str)
                        event_type = event_data.get('type')
                        
                        if event_type == 'response_final':
                            final_event_sent = True
                            logger.info(f"Request {request_id} streaming final response event " +
                                      f"(event #{events_sent + 1})")
                            # Set the final response immediately for database logging
                            # This must happen BEFORE yielding to avoid cancellation race
                            if 'data' in event_data and not request_logger.is_error:
                                request_logger.set_final_response(event_data['data'])
                                logger.debug(f"Request {request_id} final response captured for DB")
                        elif event_type == 'error':
                            error_event_sent = True
                            logger.info(f"Request {request_id} streaming error event " +
                                      f"(event #{events_sent + 1})")
                            # Capture error details for database logging
                            # The request_logger.set_error() was already called by run_agent()
                            # but we track that we successfully sent the error to the client
                            if 'data' in event_data:
                                error_type_str = event_data['data'].get(
                                    'error_type', 'UnknownError'
                                )
                                logger.debug(
                                    f"Request {request_id} error event captured: {error_type_str}"
                                )
                        elif event_type == 'retry_attempt':
                            logger.info(f"Request {request_id} streaming retry_attempt event " +
                                      f"(event #{events_sent + 1})")
                    # If json_str is empty or whitespace, just skip parsing silently
                # If event doesn't start with "data: ", skip parsing silently
                    
            except json.JSONDecodeError:
                # Only log if this seems like a real parsing issue (not empty content)
                event_preview = event[:100] if event else "(empty)"
                logger.debug(f"Request {request_id} could not parse event for logging " +
                           f"(likely empty content): {event_preview}")
            except Exception as e:
                # Log unexpected errors during event parsing
                logger.warning(f"Request {request_id} unexpected error parsing event for " +
                              f"logging: {str(e)}")
            
            # Attempt to yield the event - this is where client disconnection is often detected
            try:
                yield event
                events_sent += 1
                
                # Log periodic progress for long-running requests
                if events_sent % 100 == 0:
                    logger.info(
                        f"Request {request_id} streamed {events_sent} events " +
                        f"(final_sent: {final_event_sent}, error_sent: {error_event_sent})"
                    )
                    
            except GeneratorExit:
                # Client disconnected during event yield
                logger.warning(
                    f"Request {request_id} client disconnected during event yield " +
                    f"after {events_sent} events (final_sent: {final_event_sent}, " +
                    f"error_sent: {error_event_sent})"
                )
                raise
            except Exception as e:
                logger.error(f"Request {request_id} failed to yield event " +
                            f"#{events_sent + 1}: {str(e)}")
                raise
            
            event_queue.task_done()
            
    except asyncio.CancelledError as e:
        import traceback
        logger.error(f"Request {request_id} asyncio.CancelledError: {str(e)}")
        logger.error(
            f"Cancellation traceback for request {request_id}: {traceback.format_exc()}"
        )
        elapsed = time.time() - request_logger.start_time
        logger.error(f"Request elapsed time for request {request_id}: {elapsed:.2f}s")
        # Phase 2: Client cancelled - cancel the agent task
        logger.warning(
            f"Request {request_id} asyncio.CancelledError - client cancelled request " +
            f"after {events_sent} events (final_sent: {final_event_sent}, " +
            f"error_sent: {error_event_sent})"
        )
        
        # Phase 2: Cancel the async agent task
        if agent_task and not agent_task.done():
            logger.info(f"Request {request_id} cancelling agent task")
            agent_task.cancel()
            try:
                # Wait briefly for agent task to handle cancellation
                await asyncio.wait_for(agent_task, timeout=3.0)
                logger.info(f"Request {request_id} agent task cancelled gracefully")
            except asyncio.CancelledError:
                logger.info(f"Request {request_id} agent task cancellation completed")
            except asyncio.TimeoutError:
                logger.warning(f"Request {request_id} agent task did not cancel within timeout")
            except Exception as e:
                logger.warning(f"Request {request_id} agent task cancellation error: {str(e)}")
        else:
            logger.info(f"Request {request_id} agent task already completed when cancelled")
        
        # Try to send cancellation error response to client if possible
        try:
            cancellation_error = {
                "type": "error",
                "data": {
                    "text": "Request was cancelled by the client.",
                    "error_type": "ClientCancellation"
                },
                "request_id": request_id,
                "api_version": API_VERSION
            }
            yield format_sse_event(cancellation_error)
            logger.info(f"Request {request_id} sent cancellation error response to client")
        except Exception as e:
            logger.debug(f"Request {request_id} could not send cancellation response: {str(e)}")
        
        raise
        
    except GeneratorExit:
        # Phase 2: Another form of client disconnection
        logger.warning(
            f"Request {request_id} GeneratorExit - client disconnected " +
            f"after {events_sent} events (final_sent: {final_event_sent}, " +
            f"error_sent: {error_event_sent})"
        )
        
        # Phase 2: Cancel the async agent task
        if agent_task and not agent_task.done():
            logger.info(f"Request {request_id} cancelling agent task (GeneratorExit)")
            agent_task.cancel()
            try:
                await asyncio.wait_for(agent_task, timeout=3.0)
                logger.info(
                    f"Request {request_id} agent task cancelled gracefully after GeneratorExit"
                )
            except asyncio.CancelledError:
                logger.info(f"Request {request_id} agent task cancellation completed")
            except asyncio.TimeoutError:
                logger.warning(f"Request {request_id} agent task did not cancel within timeout")
            except Exception as e:
                logger.warning(f"Request {request_id} agent task cancellation error: {str(e)}")
        raise
        
    except Exception as e:
        # Phase 2: Streaming failed, cancel agent task
        logger.error(f"Request {request_id} streaming failed after {events_sent} events: " +
                    f"{type(e).__name__}: {str(e)}")
        if agent_task and not agent_task.done():
            logger.info(f"Request {request_id} cancelling agent task due to streaming error")
            agent_task.cancel()
        raise
    finally:
        # Phase 2: Clean up heartbeat task first
        if heartbeat and not heartbeat.done():
            logger.debug(f"Request {request_id} cancelling heartbeat task")
            heartbeat.cancel()
            try:
                await heartbeat
            except asyncio.CancelledError:
                pass  # Expected
        
        # Phase 2: Clean up agent task if needed
        if agent_task and not agent_task.done():
            logger.info(f"Request {request_id} finally block: agent task still running, cancelling")
            agent_task.cancel()
        else:
            logger.info(f"Request {request_id} finally block: agent task already completed")
        
        # Log a final termination event to ensure stream ends
        logger.info(
            f"Request {request_id} finalizing SSE stream " +
            f"(events_sent: {events_sent}, final_sent: {final_event_sent}, " +
            f"error_sent: {error_event_sent})"
        )
        
        # Finalize the database log (with protection from cancellation)
        # Note: For successful cases, this is done earlier (before stream_end)
        # But for error cases or early termination, we need to do it here
        logger.info(
            f"Request {request_id} finalizing database log " +
            f"(events_sent: {events_sent}, final_sent: {final_event_sent}, " +
            f"error_sent: {error_event_sent})"
        )
        
        # Phase 2: Log comprehensive completion status (no cancellation_flag to check)
        # Check if we sent either a successful response OR an intentional error response
        if not final_event_sent and not error_event_sent:
            # Determine likely cause based on event count and agent state
            if events_sent > 100:
                if agent_task and agent_task.done():
                    try:
                        # Check if agent completed successfully or with error
                        await agent_task
                        logger.error(
                            f"Request {request_id} completed without sending final response! " +
                            "Agent task completed successfully but response_final event was " +
                            "never processed. This suggests the client disconnection " +
                            "interrupted event streaming."
                        )
                    except asyncio.CancelledError:
                        logger.info(
                            f"Request {request_id} was cancelled by client - no final response sent"
                        )
                    except Exception as agent_error:
                        logger.error(
                            f"Request {request_id} completed without sending final response! " +
                            f"Agent task failed: {str(agent_error)}. Events sent: {events_sent}"
                        )
                else:
                    logger.error(
                        f"Request {request_id} completed without sending final response! " +
                        f"Agent task did not complete. Events sent: {events_sent}"
                    )
            else:
                logger.error(
                    f"Request {request_id} completed without sending final response! " +
                    f"Low event count ({events_sent}) suggests early termination or " +
                    "agent failure."
                )
        elif final_event_sent:
            logger.info(
                f"Request {request_id} completed successfully with final response sent"
            )
        elif error_event_sent:
            logger.info(
                f"Request {request_id} completed with error response sent (expected failure)"
            )
        
        # Shield database logging from cancellation for error cases
        # For successful cases, this was already done before sending stream_end
        try:
            await asyncio.shield(request_logger.finalize_log())
        except Exception as e:
            logger.error(f"Request {request_id} failed to finalize log in finally block: {e}")

@app.post("/respond")
async def respond(request: Request):
    """
    Endpoint to generate educational content from a prompt.
    Streams the response as Server-Sent Events.
    
    Request body:
    - prompt (required): The prompt for generating educational content
    - conversation_id (optional): ID of conversation for threading
    - user_id (optional): User ID for conversation tracking
    - model (optional): Either "incept" or "o3", defaults to "incept"
    - timeout_seconds or timeout (optional): Request timeout in seconds (1-1800), defaults to 600
    - amq_json_format (optional): If true, formats response as AMQ JSON, defaults to false
    - include_reasoning (optional): If true, streams reasoning_delta events, defaults to true
    - use_coach_bot_tools (optional): If true, uses enhanced coach-bot tools for image generation,
    defaults to false
    """
    request_id = f"req_{uuid.uuid4()}"
    
    # Parse the JSON body
    try:
        body = await request.json()
    except Exception as e:
        return create_json_response(
            content={"error": f"Invalid JSON in request body: {str(e)}", "request_id": request_id}, 
            status_code=400
        )
    
    prompt = body.get("prompt")
    conversation_id = body.get("conversation_id")
    user_id = body.get("user_id")
    model = body.get("model", "incept")
    timeout_seconds = body.get("timeout_seconds") or body.get("timeout", 600)
    amq_json_format = body.get("amq_json_format", False)
    include_reasoning = body.get("include_reasoning", False)
    
    # Validate that prompt is provided
    if not prompt:
        return create_json_response(
            content={"error": "prompt is required", "request_id": request_id}, 
            status_code=400
        )
    
    # Validate model parameter
    if model not in ["incept", "o3"]:
        return create_json_response(
            content={"error": "model must be either 'incept' or 'o3'", "request_id": request_id}, 
            status_code=400
        )
    
    # Validate timeout parameter
    if not isinstance(timeout_seconds, (int, float)) or timeout_seconds <= 0 \
        or timeout_seconds > 1800:
        return create_json_response(
            content={
                "error": "timeout_seconds must be a positive number between 1 and 1800 " + \
                         "(30 minutes max)",
                "request_id": request_id
            }, 
            status_code=400
        )
    
    # Validate include_reasoning parameter
    if not isinstance(include_reasoning, bool):
        return create_json_response(
            content={"error": "include_reasoning must be a boolean", "request_id": request_id}, 
            status_code=400
        )
    
    use_coach_bot_tools = body.get("use_coach_bot_tools", False)
    
    client_info = await get_client_info(request)
    
    conversation_info = f"conversation_id: {conversation_id}" if conversation_id \
        else "new conversation"
    amq_info = " (AMQ JSON format)" if amq_json_format else ""
    reasoning_info = "" if include_reasoning else " (reasoning streaming disabled)"
    logger.info(
        f"Received request {request_id} with model {model} using {conversation_info} from "
        f"{client_info.get('client_ip', 'unknown')} (timeout: {timeout_seconds}s){amq_info}"
        f"{reasoning_info}"
    )
        
    return EventStreamResponse(
        event_generator(
            prompt, request_id, conversation_id, user_id, model, client_info, 
            timeout_seconds, amq_json_format, include_reasoning, 
            use_coach_bot_tools
        ),
        request_id=request_id,
        media_type="text/event-stream"
    )

@app.post("/evaluate")
async def evaluate(request: Request) -> JSONResponse:
    """
    Endpoint to evaluate educational content.
    Takes a markdown string and returns an evaluation using OpenAI's GPT-4o model.
    Can optionally link the evaluation to a specific request via request_id.
    """
    request_id = f"req_{uuid.uuid4()}"
    
    # Parse the JSON body
    body = await request.json()
    content = body.get("content")
    response_id = body.get("response_id")  # Optional: link to specific request
    
    if not content:
        return create_json_response(
            content={"error": "content is required"}, 
            status_code=400
        )
    
    logger.info(f"Received evaluation request {request_id}")
    
    # Evaluate the content
    try:
        evaluation = await comprehensive_evaluate(content)
        
        # Try to link this evaluation to a request log
        target_request_id = None
        if response_id:
            # Check if this request has successful retry records
            # This ensures evaluations are logged to the actual successful attempt,
            # not the original failed attempt
            target_request_id = await find_successful_retry_record(response_id)
            if target_request_id != response_id:
                logger.info(
                    f"Linking evaluation to successful retry {target_request_id} instead of "
                    f"original {response_id}"
                )
            else:
                logger.info(f"Linking evaluation to provided response_id: {response_id}")
        else:
            # Try to find by content matching
            target_request_id = await find_request_by_content(content)
            if target_request_id:
                logger.info(f"Found matching request for evaluation: {target_request_id}")
                # Also check if this matched request has successful retries
                target_request_id = await find_successful_retry_record(target_request_id)
        
        # Update the request log with evaluation if we found a match
        if target_request_id:
            try:
                # Parse the evaluation JSON to store as JSONB
                evaluation_dict = json.loads(evaluation) if isinstance(evaluation, str) \
                    else evaluation
                await update_request_log_evaluation(target_request_id, evaluation_dict)
            except Exception as e:
                logger.error(f"Failed to update request log with evaluation: {str(e)}")
        
        return create_json_response(
            content={"evaluation": evaluation, "request_id": request_id}, 
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error evaluating content: {str(e)}")
        return create_json_response(
            content={"error": f"Error evaluating content: {str(e)}", "request_id": request_id}, 
            status_code=500
        )

@app.get("/logs/{request_id}")
async def get_log(request_id: str) -> JSONResponse:
    """
    Endpoint to retrieve a request log by request_id.
    Useful for debugging and analysis.
    """
    try:
        log_data = await get_request_log(request_id)
        
        if log_data is None:
            return create_json_response(
                content={
                    "error": f"Request log not found for {request_id}", 
                    "request_id": request_id
                }, 
                status_code=404
            )
        
        return create_json_response(
            content={"log": log_data, "request_id": request_id}, 
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error retrieving request log for {request_id}: {str(e)}")
        return create_json_response(
            content={"error": f"Error retrieving request log: {str(e)}", "request_id": request_id}, 
            status_code=500
        )

@app.get("/version")
async def get_version() -> JSONResponse:
    """
    Endpoint to retrieve the current API version.
    """
    return create_json_response(content={"version": API_VERSION}, status_code=200)

@app.post("/feedback")
async def submit_feedback(request: Request) -> JSONResponse:
    """
    Endpoint to submit feedback (rating and/or comments) for a specific request.
    
    Request body:
    - request_id (required): The ID of the request to provide feedback for
    - rating (optional): Integer rating: 1 (positive), 0 (neutral), -1 (negative)
    - comments (optional): Text comments about the response
    """
    # Parse the JSON body
    body = await request.json()
    request_id = body.get("request_id")
    rating = body.get("rating")
    comments = body.get("comments")
    
    # Validate required fields
    if not request_id:
        return create_json_response(
            content={"error": "request_id is required"}, 
            status_code=400
        )
    
    # Validate that at least one feedback field is provided
    if rating is None and comments is None:
        return create_json_response(
            content={
                "error": "At least one of 'rating' or 'comments' must be provided",
                "request_id": request_id
            }, 
            status_code=400
        )
    
    # Validate rating if provided
    if rating is not None:
        if not isinstance(rating, int) or rating not in [-1, 0, 1]:
            return create_json_response(
                content={
                    "error": "rating must be an integer: 1 (positive), 0 (neutral), or -1 " +\
                             "(negative)",
                    "request_id": request_id
                }, 
                status_code=400
            )
    
    # Validate comments if provided
    if comments is not None:
        if not isinstance(comments, str):
            return create_json_response(
                content={"error": "comments must be a string", "request_id": request_id}, 
                status_code=400
            )
        # Optionally limit comment length
        if len(comments) > 5000:  # 5000 character limit
            return create_json_response(
                content={
                    "error": "comments must be 5000 characters or less", 
                    "request_id": request_id
                }, 
                status_code=400
            )
    
    logger.info(
        f"Received feedback for request {request_id}: rating={rating}, "
        f"comments={'provided' if comments else 'none'}"
    )
    
    # Update the request log with feedback
    try:
        success = await update_request_log_feedback(request_id, rating, comments)
        
        if not success:
            return create_json_response(
                content={
                    "error": f"Request ID {request_id} not found or could not be updated",
                    "request_id": request_id
                }, 
                status_code=404
            )
        
        response_data = {
            "message": "Feedback submitted successfully",
            "request_id": request_id
        }
        
        # Include what was updated in the response
        if rating is not None:
            response_data["rating"] = rating
        if comments is not None:
            response_data["comments_received"] = True
            
        return create_json_response(content=response_data, status_code=200)
        
    except Exception as e:
        logger.error(f"Error submitting feedback for {request_id}: {str(e)}")
        return create_json_response(
            content={"error": f"Error submitting feedback: {str(e)}", "request_id": request_id}, 
            status_code=500
        )

@app.post("/convert-to-qti")
async def convert_to_qti(request: Request) -> FileResponse:
    """
    Endpoint to convert markdown educational content to QTI 3.0 format.
    
    Request body:
    - content (required): Markdown formatted assessment content
    - timeout_seconds (optional): Request timeout in seconds (1-1800), defaults to 600
    
    Returns:
    - ZIP file containing the QTI package with manifest and any referenced images
    """
    request_id = f"qti_{uuid.uuid4()}"
    
    # Parse the JSON body
    try:
        body = await request.json()
    except Exception as e:
        logger.error(f"🎯 Failed to parse JSON body: {e}")
        return create_json_response(
            content={"error": f"Invalid JSON in request body: {str(e)}", "request_id": request_id}, 
            status_code=400
        )
    
    content = body.get("content")
    timeout_seconds = body.get("timeout_seconds", 180)  # Default 3 minutes
    
    if not content:
        return create_json_response(
            content={"error": "content is required", "request_id": request_id}, 
            status_code=400
        )
    
    # Validate timeout parameter
    if not isinstance(timeout_seconds, (int, float)) or timeout_seconds <= 0 \
        or timeout_seconds > 1800:
        return create_json_response(
            content={
                "error": "timeout_seconds must be a positive number between 1 and 1800 " + \
                         "(30 minutes max)",
                "request_id": request_id
            }, 
            status_code=400
        )
    
    # Collect client information for logging
    client_info = await get_client_info(request)
    
    logger.info(
        f"Received QTI conversion request {request_id} from "
        f"{client_info.get('client_ip', 'unknown')} (timeout: {timeout_seconds}s)"
    )
    
    # Retry logic similar to the respond endpoint
    max_retries = 2
    retry_count = 0
    start_time = time.time()
    
    while retry_count <= max_retries:
        # Check if we've exceeded the total timeout
        elapsed_time = time.time() - start_time
        if elapsed_time >= timeout_seconds:
            logger.error(f"QTI conversion {request_id}: Exceeded {timeout_seconds}s timeout")
            return create_json_response(
                content={
                    "error": f"Request exceeded maximum timeout of {timeout_seconds} seconds. " + \
                             "Please try again with a simpler request or increase the timeout.",
                    "error_type": "RequestTimeout",
                    "request_id": request_id
                }, 
                status_code=504
            )
        
        try:
            # Get the QTI tool
            qti_spec, qti_function = generate_qti_tool()
            
            # Generate the QTI package
            logger.info(
                f"QTI conversion {request_id}: Starting conversion (attempt "
                f"{retry_count + 1}/{max_retries + 1})"
            )
            package_path = await qti_function(content)
            
            # Verify the file exists
            if not os.path.exists(package_path):
                logger.error(
                    f"QTI conversion {request_id}: Generated package not found at {package_path}"
                )
                return create_json_response(
                    content={"error": "Failed to generate QTI package", "request_id": request_id}, 
                    status_code=500
                )
            
            # Generate a friendly filename
            filename = f"qti_package_{request_id}.zip"
            
            logger.info(
                f"QTI conversion {request_id}: Sending package {package_path} as {filename}"
            )
            
            # Return the ZIP file
            return FileResponse(
                path=package_path,
                filename=filename,
                media_type="application/zip",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}",
                    "Content-Type": "application/zip"
                }
            )
            
        except (APITimeoutError, TimeoutException, ReadTimeout, WriteTimeout, ConnectTimeout, 
                socket.timeout if socket else type(None), 
                requests.exceptions.Timeout if requests else type(None),
                requests.exceptions.ConnectionError if requests else type(None)) as e:
            retry_count += 1
            error_msg = f"Timeout error in QTI conversion for request {request_id} (attempt " + \
                        f"{retry_count}/{max_retries + 1}): {type(e).__name__}: {str(e)}"
            logger.warning(error_msg)
            
            if retry_count <= max_retries:
                # Wait a bit before retrying
                backoff_time = min(2 ** retry_count, 10)
                logger.info(
                    f"QTI conversion {request_id} waiting {backoff_time}s before retry "
                    f"{retry_count + 1}"
                )
                time.sleep(backoff_time)  # Exponential backoff, max 10 seconds
                continue
            else:
                # Final timeout error after all retries
                logger.error(
                    f"QTI conversion {request_id}: Timeout after {max_retries + 1} attempts"
                )
                return create_json_response(
                    content={
                        "error": "The request timed out after multiple attempts. This may be " + \
                                 "due to high demand or complex content. Please try again " + \
                                 "with simpler content or try again later.",
                        "error_type": "TimeoutError",
                        "request_id": request_id
                    }, 
                    status_code=504
                )
                
        except APIError as e:
            # Handle OpenAI API errors - retry if it seems like a transient error
            error_str = str(e).lower()
            is_retryable_api_error = any(phrase in error_str for phrase in [
                'error occurred while processing the request',
                'internal server error',
                'service unavailable',
                'temporarily unavailable',
                'please try again'
            ])
            
            if is_retryable_api_error and retry_count < max_retries:
                retry_count += 1
                logger.warning(
                    f"Retryable API error in QTI conversion for request {request_id} (attempt "
                    f"{retry_count}/{max_retries + 1}): {type(e).__name__}: {str(e)}"
                )
                
                # Wait a bit before retrying
                backoff_time = min(2 ** retry_count, 10)
                logger.info(
                    f"QTI conversion {request_id} waiting {backoff_time}s before retry "
                    f"{retry_count + 1}"
                )
                time.sleep(backoff_time)
                continue
            else:
                # Non-retryable API error or max retries exceeded
                if is_retryable_api_error:
                    logger.error(
                        f"API error in QTI conversion for request {request_id} - max retries "
                        f"exceeded: {type(e).__name__}: {str(e)}"
                    )
                    error_message = "The AI service encountered repeated errors. Please try " + \
                                     "again in a few moments."
                    error_type = "RepeatedAPIError"
                else:
                    logger.error(
                        f"Non-retryable API error in QTI conversion for request {request_id}: "
                        f"{type(e).__name__}: {str(e)}"
                    )
                    error_message = "The AI service encountered an error processing your " + \
                                     "request. Please try again or try with simpler content."
                    error_type = "APIError"
                
                return create_json_response(
                    content={
                        "error": error_message,
                        "error_type": error_type,
                        "request_id": request_id
                    }, 
                    status_code=500
                )
        
        except Exception as e:
            # Handle any other errors during conversion
            import traceback
            full_traceback = traceback.format_exc()
            logger.error(
                f"Non-timeout error in QTI conversion for request {request_id}: "
                f"{type(e).__name__}: {str(e)}"
            )
            logger.error(f"Full traceback for QTI conversion {request_id}:\n{full_traceback}")
            
            # Check if this might be a timeout-related error we didn't catch
            error_str = str(e).lower()
            if any(timeout_keyword in error_str for timeout_keyword \
                in ['timeout', 'timed out', 'read timeout', 'connection timeout']):
                logger.warning(
                    f"QTI conversion {request_id} appears to be a timeout error but wasn't caught "
                    f"by timeout handlers: {type(e).__name__}: {str(e)}"
                )
                
                # Treat as timeout and retry if we haven't exceeded max retries
                if retry_count < max_retries:
                    retry_count += 1
                    logger.info(
                        f"QTI conversion {request_id} treating as timeout, attempting retry "
                        f"{retry_count + 1}/{max_retries + 1}"
                    )
                    
                    backoff_time = min(2 ** retry_count, 10)
                    logger.info(
                        f"QTI conversion {request_id} waiting {backoff_time}s before retry "
                        f"{retry_count + 1}"
                    )
                    time.sleep(backoff_time)
                    continue
            
            # Determine user-friendly error message based on error type
            if isinstance(e, RateLimitError):
                error_message = "The service is currently experiencing high demand. Please try " + \
                                 "again in a few moments."
                error_type = "RateLimitError"
            elif isinstance(e, APIConnectionError):
                error_message = "Unable to connect to the AI service. Please check your " + \
                                 "connection and try again."
                error_type = "ConnectionError"
            elif "download" in str(e).lower() or "image" in str(e).lower():
                error_message = "Error downloading images from the content. Please check " + \
                                 "image URLs."
                error_type = "ImageDownloadError"
            else:
                error_message = f"Error generating QTI package: {str(e)}"
                error_type = type(e).__name__
            
            return create_json_response(
                content={
                    "error": error_message,
                    "error_type": error_type,
                    "request_id": request_id
                }, 
                status_code=500
            )
    
    # This should never be reached, but just in case
    return create_json_response(
        content={
            "error": "Unexpected error: exceeded maximum retry attempts",
            "error_type": "UnexpectedError",
            "request_id": request_id
        }, 
        status_code=500
    )

@app.post("/convert-to-athena")
async def convert_to_athena(request: Request) -> JSONResponse:
    """
    Endpoint to convert markdown educational content to structured JSON format using Athena
    formatter.
    
    Request body:
    - content (required): Markdown formatted educational content
    - timeout_seconds (optional): Request timeout in seconds (1-1800), defaults to 600
    
    Returns:
    - JSON object containing the structured content conforming to MultipleChoiceQuestion schema
    """
    request_id = f"athena_{uuid.uuid4()}"
    
    # Parse the JSON body
    try:
        body = await request.json()
    except Exception as e:
        logger.error(f"🎯 Failed to parse JSON body: {e}")
        return create_json_response(
            content={"error": f"Invalid JSON in request body: {str(e)}", "request_id": request_id}, 
            status_code=400
        )
    
    content = body.get("content")
    timeout_seconds = body.get("timeout_seconds", 180)  # Default 3 minutes
    
    if not content:
        return create_json_response(
            content={"error": "content is required", "request_id": request_id}, 
            status_code=400
        )
    
    # Validate timeout parameter
    if not isinstance(timeout_seconds, (int, float)) or timeout_seconds <= 0 \
        or timeout_seconds > 1800:
        return create_json_response(
            content={
                "error": "timeout_seconds must be a positive number between 1 and 1800 (30 " + \
                         "minutes max)",
                "request_id": request_id
            }, 
            status_code=400
        )
    
    # Collect client information for logging
    client_info = await get_client_info(request)
    
    logger.info(
        f"Received Athena conversion request {request_id} from "
        f"{client_info.get('client_ip', 'unknown')} (timeout: {timeout_seconds}s)"
    )
    
    # Retry logic similar to the respond endpoint
    max_retries = 2
    retry_count = 0
    start_time = time.time()
    
    while retry_count <= max_retries:
        # Check if we've exceeded the total timeout
        elapsed_time = time.time() - start_time
        if elapsed_time >= timeout_seconds:
            logger.error(f"Athena conversion {request_id}: Exceeded {timeout_seconds}s timeout")
            return create_json_response(
                content={
                    "error": f"Request exceeded maximum timeout of {timeout_seconds} seconds. " + \
                             "Please try again with a simpler request or increase the timeout.",
                    "error_type": "RequestTimeout",
                    "request_id": request_id
                }, 
                status_code=504
            )
        
        try:
            # Get the Athena formatter tool
            athena_spec, athena_function = generate_athena_formatter_tool()
            
            # Convert the content to structured JSON
            logger.info(
                f"Athena conversion {request_id}: Starting conversion (attempt "
                f"{retry_count + 1}/{max_retries + 1})"
            )
            structured_json = athena_function(content)
            
            # Parse the JSON string to verify it's valid JSON
            try:
                parsed_json = json.loads(structured_json)
            except json.JSONDecodeError as e:
                logger.error(f"Athena conversion {request_id}: Generated invalid JSON: {e}")
                return create_json_response(
                    content={
                        "error": "Generated invalid JSON structure", 
                        "request_id": request_id
                    }, 
                    status_code=500
                )
            
            logger.info(f"Athena conversion {request_id}: Conversion completed successfully")
            
            # Return the structured JSON
            return create_json_response(content={
                "request_id": request_id,
                "structured_content": parsed_json
            }, status_code=200)
            
        except (APITimeoutError, TimeoutException, ReadTimeout, WriteTimeout, ConnectTimeout, 
                socket.timeout if socket else type(None), 
                requests.exceptions.Timeout if requests else type(None),
                requests.exceptions.ConnectionError if requests else type(None)) as e:
            retry_count += 1
            error_msg = f"Timeout error in Athena conversion for request {request_id} (attempt " + \
                        f"{retry_count}/{max_retries + 1}): {type(e).__name__}: {str(e)}"
            logger.warning(error_msg)
            
            if retry_count <= max_retries:
                # Wait a bit before retrying
                backoff_time = min(2 ** retry_count, 10)
                logger.info(
                    f"Athena conversion {request_id} waiting {backoff_time}s before retry "
                    f"{retry_count + 1}"
                )
                time.sleep(backoff_time)  # Exponential backoff, max 10 seconds
                continue
            else:
                # Final timeout error after all retries
                logger.error(
                    f"Athena conversion {request_id}: Timeout after {max_retries + 1} attempts"
                )
                return create_json_response(
                    content={
                        "error": "The request timed out after multiple attempts. This may be " + \
                                 "due to high demand or complex content. Please try again " + \
                                 "with simpler content or try again later.",
                        "error_type": "TimeoutError",
                        "request_id": request_id
                    }, 
                    status_code=504
                )
                
        except APIError as e:
            # Handle OpenAI API errors - retry if it seems like a transient error
            error_str = str(e).lower()
            is_retryable_api_error = any(phrase in error_str for phrase in [
                'error occurred while processing the request',
                'internal server error',
                'service unavailable',
                'temporarily unavailable',
                'please try again'
            ])
            
            if is_retryable_api_error and retry_count < max_retries:
                retry_count += 1
                logger.warning(
                    f"Retryable API error in Athena conversion for request {request_id} (attempt "
                    f"{retry_count}/{max_retries + 1}): {type(e).__name__}: {str(e)}"
                )
                
                # Wait a bit before retrying
                backoff_time = min(2 ** retry_count, 10)
                logger.info(
                    f"Athena conversion {request_id} waiting {backoff_time}s before retry "
                    f"{retry_count + 1}"
                )
                time.sleep(backoff_time)
                continue
            else:
                # Non-retryable API error or max retries exceeded
                if is_retryable_api_error:
                    logger.error(
                        f"API error in Athena conversion for request {request_id} - max retries "
                        f"exceeded: {type(e).__name__}: {str(e)}"
                    )
                    error_message = "The AI service encountered repeated errors. Please try " + \
                                     "again in a few moments."
                    error_type = "RepeatedAPIError"
                else:
                    logger.error(
                        f"Non-retryable API error in Athena conversion for request {request_id}: "
                        f"{type(e).__name__}: {str(e)}"
                    )
                    error_message = "The AI service encountered an error processing your " + \
                                     "request. Please try again or try with simpler content."
                    error_type = "APIError"
                
                return create_json_response(
                    content={
                        "error": error_message,
                        "error_type": error_type,
                        "request_id": request_id
                    }, 
                    status_code=500
                )
        
        except UnknownContentTypeError as e:
            logger.warning(f"Unknown content type for Athena conversion {request_id}: {str(e)}")
            return create_json_response(
                content={
                    "error": "Unable to determine the content type from the provided markdown. " + \
                             "Please ensure the content contains a clear question format.",
                    "details": str(e),
                    "request_id": request_id
                }, 
                status_code=422
            )
            
        except UnsupportedContentTypeError as e:
            logger.warning(f"Unsupported content type for Athena conversion {request_id}: {str(e)}")
            return create_json_response(
                content={
                    "error": "The content type is not currently supported for structured " + \
                             "conversion. Currently supported: Multiple Choice Questions and " + \
                             "Text Entry Questions.",
                    "details": str(e),
                    "request_id": request_id
                }, 
                status_code=422
            )
            
        except Exception as e:
            # Handle any other errors during conversion
            import traceback
            full_traceback = traceback.format_exc()
            logger.error(
                f"Non-timeout error in Athena conversion for request {request_id}: "
                f"{type(e).__name__}: {str(e)}"
            )
            logger.error(f"Full traceback for Athena conversion {request_id}:\n{full_traceback}")
            
            # Check if this might be a timeout-related error we didn't catch
            error_str = str(e).lower()
            if any(timeout_keyword in error_str for timeout_keyword \
                in ['timeout', 'timed out', 'read timeout', 'connection timeout']):
                logger.warning(
                    f"Athena conversion {request_id} appears to be a timeout error but wasn't "
                    f"caught by timeout handlers: {type(e).__name__}: {str(e)}"
                )
                
                # Treat as timeout and retry if we haven't exceeded max retries
                if retry_count < max_retries:
                    retry_count += 1
                    logger.info(
                        f"Athena conversion {request_id} treating as timeout, attempting retry "
                        f"{retry_count + 1}/{max_retries + 1}"
                    )
                    
                    backoff_time = min(2 ** retry_count, 10)
                    logger.info(
                        f"Athena conversion {request_id} waiting {backoff_time}s before retry "
                        f"{retry_count + 1}"
                    )
                    time.sleep(backoff_time)
                    continue
            
            # Determine user-friendly error message based on error type
            if isinstance(e, RateLimitError):
                error_message = "The service is currently experiencing high demand. Please try " + \
                                 "again in a few moments."
                error_type = "RateLimitError"
            elif isinstance(e, APIConnectionError):
                error_message = "Unable to connect to the AI service. Please check your " + \
                                 "connection and try again."
                error_type = "ConnectionError"
            else:
                error_message = f"Error converting to structured format: {str(e)}"
                error_type = type(e).__name__
            
            return create_json_response(
                content={
                    "error": error_message,
                    "error_type": error_type,
                    "request_id": request_id
                }, 
                status_code=500
            )
    
    # This should never be reached, but just in case
    return create_json_response(
        content={
            "error": "Unexpected error: exceeded maximum retry attempts",
            "error_type": "UnexpectedError",
            "request_id": request_id
        }, 
        status_code=500
    )

@app.get("/health")
async def health_check() -> JSONResponse:
    """
    Health check endpoint to verify the API is running.
    Returns 503 if the service is shutting down to help load balancers.
    """
    global shutdown_flag
    
    if shutdown_flag:
        return create_json_response(content={
            "status": "shutting_down", 
            "timestamp": time.time()
        }, status_code=503)
    
    return create_json_response(content={
        "status": "healthy", 
        "timestamp": time.time()
    }, status_code=200)

@app.get("/system-status")
async def system_status():
    """System resource monitoring endpoint."""
    try:
        # Memory usage
        memory = psutil.virtual_memory()
        process = psutil.Process()
        process_memory = process.memory_info()
        
        # Phase 2: Async task information (no thread pool)
        # Count all running async tasks
        all_tasks = asyncio.all_tasks()
        running_tasks = len([t for t in all_tasks if not t.done()])
        
        async_info = {
            "architecture": "pure_async",
            "total_tasks": len(all_tasks),
            "running_tasks": running_tasks,
            "note": "No thread pool - using asyncio for all concurrent operations"
        }
        
        return create_json_response(content={
            "status": "healthy",
            "version": API_VERSION,
            "system_memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "percent_used": memory.percent,
                "process_rss_mb": round(process_memory.rss / (1024**2), 1),
                "process_vms_mb": round(process_memory.vms / (1024**2), 1)
            },
            "swap_memory": {
                "total_gb": round(psutil.swap_memory().total / (1024**3), 2),
                "percent_used": psutil.swap_memory().percent
            },
            "async_runtime": async_info,
            "timestamp": time.time()
        }, status_code=200)
    except Exception as e:
        return create_json_response(content={
            "status": "error",
            "error": str(e),
            "version": API_VERSION,
            "timestamp": time.time()
        }, status_code=500)

@app.get("/api-keys/stats")
async def get_api_key_stats() -> JSONResponse:
    """
    Get API key usage statistics.
    
    Returns information about:
    - Total number of API keys
    - Usage counts per key
    - Last usage timestamps
    """
    try:
        stats = get_api_key_manager().get_usage_stats()
        return create_json_response(content=stats, status_code=200)
    except Exception as e:
        logger.error(f"Error getting API key stats: {e}")
        return create_json_response(content={
            "error": "Failed to retrieve API key statistics",
            "details": str(e)
        }, status_code=500)

@app.get("/qc-stats")
async def get_qc_stats_endpoint() -> JSONResponse:
    """
    Get Quality Control system statistics.
    
    Returns information about:
    - Chrome pool status and usage
    - Screenshot caching performance  
    - Concurrency and error metrics
    - Instance lifecycle statistics
    """
    try:
        stats = get_qc_stats()
        return create_json_response(content=stats, status_code=200)
    except Exception as e:
        logger.error(f"Error getting QC stats: {e}")
        return create_json_response(content={
            "error": "Failed to retrieve QC statistics",
            "details": str(e)
        }, status_code=500)