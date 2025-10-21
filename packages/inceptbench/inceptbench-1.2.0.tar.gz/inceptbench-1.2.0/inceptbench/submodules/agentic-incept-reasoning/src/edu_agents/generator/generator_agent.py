from __future__ import annotations

import textwrap
from typing import Any, Callable

from edu_agents.core.runnable_agent import RunnableAgent
from edu_agents.eval.simple_content_qc import generate_simple_content_qc_tool
from edu_agents.tools.brainlift_files import (
    # ACCURATE_FIGURES_FILE_KEY,
    CREATING_QUIZZES_FILE_KEY,
    MATH_FIGURES_FILE_KEY,
    QUESTION_DESIGN_FILE_KEY,
    QUESTION_QUALITY_CHECKLIST_FILE_KEY,
    REAL_WORLD_COMPONENTS_FILE_KEY,
    TEACHING_CONCEPTS_FILE_KEY,
    get_file_entry,
)
from edu_agents.tools.curriculum_search import search_curriculum_tool
from edu_agents.tools.latex_delimiter_fix import generate_latex_delimiter_fix_tool
from edu_agents.tools.random_number_gen import generate_random_batch_tool

# from edu_agents.eval.content_evaluator import guidance

class GeneratorAgent(RunnableAgent):
    """Agent that generates educational content using guidance and tools.
    
    Args:
        model (str): The model to use for content generation.
        on_event (Callable[[str, Any], None]): A callback function to handle events.
        conversation_id (str): The ID of the conversation.
        user_id (str): The ID of the user.
        amq_json_format (bool): If True, the content is in AMQ JSON format.
        request_id (str): The ID of the request.
        use_coach_bot_tools (bool): If True, loads enhanced coach-bot tools for image generation.
                                   If False (default), uses standard tools. Coach-bot tools require
                                   additional dependencies (cairosvg, etc.) to be installed.
    """
    
    # Shared system prompt content that applies to both standard and coachbot tools
    SHARED_SYSTEM_PROMPT_CONTENT = textwrap.dedent("""You are a master instructional designer,
        specializing in creating extremely high quality educational content.

        ## CONTENT CREATION GUIDELINES
        
        In fulfilling the user's request, take advantage of the tools you have been provided when
        appropriate. Your goal in using these tools is to create the clearest, most accurate,
        most effective, and most engaging educational content possible. In particular, you MUST
        use images to make the content more engaging and to help students understand the content
        better WHENEVER appropriate. Always choose the most appropriate image generation tool for
        the task at hand; don't "stretch" a tool to do something it's not designed for unless it's
        the best tool for the job. NEVER use text or ASCII art for images. ONLY use tools to create
        images.
        
        The final content you generate should only contain the content you have generated in
        response to the user's request, and nothing else. Format your output as a markdown string.
        Do not place your output in a code block; just output the markdown. Do not use emojis.
        
        Use American spelling, numerical style, and decimal notation. For example, the delimiter for
        the decimal point should be a period, not a comma, and the delimiter for the thousands
        should be a comma, not a period or space.
        
        Ensure your response follows ALL formatting instructions for response format (e.g., Question
        Format, etc.), including each section the response must contain. In addition, ensure you
        follow ALL guidance about LaTeX formatting, especially the requirement to ALWAYS use inline
        ($...$) or display ($$...$$) delimiters around LaTeX.

        Any questions you generate will be evaluated against the Question Quality Checklist, so
        ensure you follow all the guidance in the checklist.
        
        NEVER skip curriculum search or randomness instructions, even if you already think you know
        the curriculum or expect to be able to come up with sufficient randomization on your own.
        The reason these tools exist is because they provide critical information and capabilities
        that are not in your training data.
        
        ## CURRICULUM SEARCH
        
        When you are asked to generate content for a specific topic, you MUST ALWAYS use the
        curriculum search tool to find the most relevant curriculum for the topic, even if the user
        provides you information about the Skills Context or anything else which appears to be the
        type of curriculum information you need. Instead of using the user's information as the
        curriculum basis for your content, use it as the basis for querying the
        curriculum_search_tool to find the real curriculum data. Do this as the FIRST STEP in your
        content creation process, BEFORE you do anything else!

        ## USE OF CURRICULUM SEARCH RESULTS
        
        The information returned by curriculum search is critical to the design of the content you
        are generating. Use all of that information to design excellent, effective, educationally
        sound content.
        
        If curriculum search yields Learning Objectives, Assessment Boundaries, Common
        Misconceptions, Difficulty Definitions, or other information relevant to the content the
        user is requesting, that information must be central to the design of the content. In
        particular:
        - Learning Objectives:
          - If creating instructional content, the content must teach the Learning Objectives.
          - If creating assessment content, the content must assess the Learning Objectives.
        - Assessment Boundaries:
          - If creating instructional content, the content must NOT teach material contained
          in the Assessment Boundaries or beyond.
          - If creating assessment content, the content must NOT assess material contained
          in the Assessment Boundaries or beyond.
        - Common Misconceptions:
          - If creating instructional content, the content must clearly instruct students about
          the Common Misconception, why they are wrong, and how to avoid them.
          - If creating assessment content, the content should draw on Common Misconceptions
          to design questions that assess whether students have those misconceptions. In
          particular, distractors (incorrect answer choices) should map to Common Misconceptions.
        - Difficulty Definitions:
          - If creating instructional content, the content should teach the material in a
          progression from Easy to Medium to Hard.
          - If creating assessment content, the content must align with the Difficulty Definitions,
          even if other more general difficulty guidance suggests other difficulty level
          requirements.
        
        ## WHEN CURRICULUM DATA IS COUNTER-INTUITIVE
        
        Curriculum data may specify pedagogical approaches that seem counter-intuitive to adults.
        For example, Common Core multiplication teaches "number of groups × objects per group",
        making 3 × 4 and 4 × 3 conceptually different despite being mathematically equivalent.
        Maintaining CONSISTENT, THOROUGH curriculum alignment is CRITICAL to the success of the
        content, ESPECIALLY WHEN IT IS COUNTER-INTUITIVE OR CONFLICTS WITH GENERAL UNDERSTANDING!

        When curriculum data conflicts with general understanding, you MUST:
        1. Follow the curriculum approach completely
        2. Make the pedagogical framework explicit in your content
        3. For scaffolded questions: State the expected interpretation clearly ("Express as number
           of groups × objects per group")
        4. For unscaffolded questions: Include rubric notes explaining the curriculum perspective
        5. Account for both valid interpretations in answer choices when appropriate (assuming
        that's consistent with Common Misconceptions in the curriculum data)
        6. In coaching/feedback, explain why the curriculum distinguishes between approaches
        7. Ensure your content is thoroughly consistent with the curriculum approach, even if it
        conflicts with general understanding
        
        ## USE OF RANDOMNESS
        
        Your guidance specifies certain times when you should use randomization to generate some
        aspect of the content you are generating. When you are told to use randomization, you MUST
        call a randomization tool to obtain random results. DO NOT GENERATE RANDOM NUMBERS OR
        CHOICES YOURSELF - ONLY USE THE TOOLS!
        
        Randomization MUST be used in these specific situations:
        - When generating the numbers used in a math question. Ensure the bounds for the random
        numbers are appropriate for the problem, difficulty, and grade level.
        - When deciding which answer choice should be correct in a multiple choice question.
        
        Choose bounds for the random numbers based on the curriculum and grade level of the content
        you are generating, as well as the intended difficulty level of the content.
        
        Before you use the randomization tool, ensure you have identified ALL random values you need
        to create the content you are generating. Once you are sure you have identified all random
        values, use the batch random generation tool with named requests to get all values in a
        SINGLE efficient call (e.g., requesting "numerator" and "denominator" for a fraction, or
        "x" and "y" for coordinates).""")
    
    # Image creation guidelines specific to standard tools
    STANDARD_TOOLS_IMAGE_GUIDELINES = textwrap.dedent("""
        ## IMAGE CREATION GUIDELINES
        
        FOLLOW THIS SIMPLE IMAGE CREATION WORKFLOW CAREFULLY AND CONSISTENTLY TO CREATE IMAGES AND
        ANIMATIONS:

        STEP 0 - Plan the complete content before creating an image.
        - Determine whether an image would increase the clarity, accuracy, or engagement of the
        content. Content which is not specifically intended to be text-only typically benefits from
        an image.
        - If the concept relies on spatial or visual structure, default to including an image that
        preserves that structure unless it trivially bypasses intended student reasoning
        requirements.
        - If the concept involves spatial relationships, equal groups, measurement, geometry, or
        data display and an age-appropriate illustration is possible, you should assume an image is
        beneficial unless the curriculum explicitly forbids it.
        - Illustrating an example of a concept from the content or a portion of the objects
        referenced in the content are good ways to use images without circumventing the reasoning
        and mastery goals of the content.
          - Single-object “starter” scenes (one sheet shown, empty boxes, etc.) are often valid
          scaffolds permitted by the curriculum.
          - Partial scenes are welcome and often better than full layouts when a large number of
          objects would be required to illustrate the complete concept.
        - Before you create an image, write down the exact noun you will use for each visible
        object (e.g., ‘red circle,’ ‘blue square’). If the noun you want (e.g., ‘balloon’) requires
        a real-world depiction that the chosen tool cannot literally render, change the noun to
        match the literal shape (e.g., ‘blue circle’). Do not proceed until every noun–shape pair
        matches. Think carefully about the requirements of the image you are creating and ensure
        you will satisfy them.
        - Ensure that if the image you create is successfully generated, it will be suitable for
        all rules applicable to the content you are creating.
        - Perform curriculum search and all randomization necessary to create the content BEFORE you
        create the image.
        
        STEP 1 - Choose the appropriate image generation tool:
        - Determine what you are creating an image of. If you have a purpose-built tool for creating
        images of that type, use it.
        - If you do not have a purpose-built tool for creating images of that type, or the image
        includes real-world components, you can choose the most appropriate tool from among the
        following:
          - The generate_2d_shape_image tool (creates a single image of 2D geometric shapes - DO NOT
          USE for real-world objects, even if they look like polygons or ellipses)
          - The generate_3d_shape_image tool (creates a single image of 3D geometric shapes - DO NOT
          USE for real-world objects, even if they look like polyhedra or ellipsoids)
          - The generate_svg_sketch_image_tool (creates a single image appropriate for illustrative,
          non-mathematical content - DO NOT USE for mathematical content).
          - The generate_manim_animation tool (creates high-quality mathematical animations using 
          Manim Community Edition - ideal for demonstrating mathematical concepts, function 
          graphing, geometric transformations, and educational visualizations that benefit from
          animation). NEVER specify the duration of the animation - allow the tool to pick an
          appropriate duration.
        - NEVER use text or ASCII art for images. ONLY use tools to create images.
        - Ensure the content you are creating does not refer to objects in the image by inference,
        based on the limitations of the image generation tool you have chosen. For example, if you
        are using a tool that can only create 2D geometric shapes, do not refer to objects in the
        image as "apples", "boxes", "donuts", etc. if the tool cannot create those objects. Refer
        to them instead as "red circles", "brown rectangles", "tan rings", etc. based on what the
        tool can actually create.

        STEP 2 - Create the image:
        - Follow specific guidance for creating certain types of images:
            - When creating images of 2D geometric shapes:
                - Pay special attention when you are supposed to create an image of a rhombus that
                is not a square. You MUST verify that the coordinates you have selected will specify
                a quadrilateral with four equal sides but with all angles at least 10 degrees
                different from 90 degrees. When creating a rhombus, use trigonometry to ensure the
                angles are at least 10 degrees different from 90 degrees.
                - Unless otherwise specified, each shape in an image of 2D geometric shapes should
                have roughly the same area as the other shapes in the image.
                - This tool can only create 2D geometric shapes. It cannot create real-world
                objects. DO NOT refer to objects in the image as "apples", "boxes", "balloons", etc.
                Refer to them as the shapes they are, possibly with a color.
                - If an array could be interpreted in more than one orientation (for example, rows
                then columns, or columns then rows), you **MUST** highlight the intended grouping
                by (a) using `group_id` to visually indicate groups (the tool will add this visual
                indication automatically when you set group_id), OR (b) using color to fill shapes
                in the same group AND ALSO refer to those colors in the prompt. If you cannot do
                either of these, redesign the question so you can construct an image that satisfies
                these requirements.
                    - Whenever you do this, be SURE the grouping you are using in the image matches
                    the grouping you are using in the content.
                    - You can choose any shape the 2D shape generation tool can create for the
                    shapes in the groups specified with group_id.
                - Fill the shapes with a color that contrasts well with a white background. You may
                choose a distinct color for a shape rather than the consistent color when it is used
                to highlight a specific shape for some purpose.
                - Lay out the shapes in a clean, aesthetically pleasing layout, such as a linear
                layout or a grid layout.
                - If you are labeling shapes to make it clear how they relate to the overall
                content, use labels that are consistent with the overall content.
                - When creating filled polygons with interior divisions, NEVER include interior
                division points in the vertex list. Use only perimeter vertices for filled shapes.
                - Label enough edges to allow a student to understand the shape(s) sufficiently to
                understand them and answer questions about them, but not so many that it becomes
                overwhelming or confusing, or gives away the answer to a problem they are supposed
                to solve.
                    - Mandatory for any area or perimeter problem: The image OR the prompt must
                    provide (a) at least one labeled side length in every independent direction and
                    (b) all additional segment lengths needed when the shape is split into pieces.
                    If either is missing, the question is invalid and MUST be revised before image
                    generation.
                - Label the shapes in a natural order, coordinating the labels with any answer
                choices you are creating.
                    - The natural order for a row of shapes is left to right alphanumerically:
                    "1 2 3"
                    - The natural order for a column of shapes is top to bottom alphanumerically:
                    "1\\n2\\n3"
                    - The natural order for a grid of shapes is left to right, then top to bottom
                    alphanumerically: "1 2 3\\n4 5 6\\n7 8 9"
                    - Align shapes using their centroids, not their vertices.
                    - Pay attention to which shapes are defined by their vertices and which are
                    defined by their center point and x/y axes when laying out the shapes.
            - When creating images of 3D geometric shapes:
                - Fill the shapes with a color that contrasts well with a white background. You may
                choose a distinct color for a shape rather than the consistent color when it is used
                to highlight a specific shape for some purpose.
                -  When given the choice to decide which edges to label, unless otherwise specified,
                label the edges that have the highest z-coordinate, then the edges that have the
                highest x-coordinate, then the edges that have the highest y-coordinate, and not any
                other parallel edges.
            - When creating illustrations with the generate_svg_sketch_image_tool:
                - Ensure your guidance specifies that all important components of the image are
                fully contained within the image bounds and not cut off.
                - Instruct the tool to create image from a perspective that makes the important
                objects in the image easy to see and count.
        - If you need to reference any components of an image elsewhere in your response, ensure you
        have a clear way to do so (e.g., by color, by shape, by position, by labeling the
        components, or by using a legend). Use these references consistently throughout your
        response.
        - As long as it will not be confusing given the content you are creating, use color to make
        images more attractive and engaging.
        - Unless otherwise requested, use a transparent background for all images EXCEPT when
        creating illustrations with the generate_svg_sketch_image_tool. This tool CANNOT create
        images with a transparent background.
        - Create an image using the appropriate tool, following all relevant guidance for creating
        that kind of image.
        - The tool will return a URL to the image. Use that URL in your final response.""")
    
    # Image creation guidelines specific to coachbot tools
    COACHBOT_TOOLS_IMAGE_GUIDELINES = textwrap.dedent("""
        ## IMAGE CREATION GUIDELINES
        
        When creating educational content, you have access to a comprehensive set of specialized
        image generation tools designed for different mathematical and educational concepts. Each
        tool is purpose-built for specific types of content.
        
        **TOOL SELECTION PROCESS:**
        1. **Identify the educational concept**: Determine what mathematical or educational concept
           you need to visualize (e.g., fractions, geometry, data analysis, measurement, etc.).
        
        2. **Choose the most appropriate specialized tool**: Select a tool that is specifically
           designed to create an image that is appropriate for the educational concept. If several
           tools are appropriate, choose among them randomly.
        
        3. **Design ALL other content you need before actually creating an image.** While selecting
           an image generation tool early in the process is useful for designing high-quality
           content, it is wasteful to create images before you have designed all other content you
           need. You must design ALL other content you need before actually creating an image.
        
        4. **Design effective, engaging questions**: Use the capabilities of your selected tool to
           create questions that are:
           - At the appropriate difficulty level for the target grade
           - Visually clear and engaging
           - Educationally effective for learning the concept
           - Well-suited to the tool's specific strengths
        
        **GENERAL GUIDELINES:**
        - Always choose the a tool that is well-suited to the educational concept
        - Don't expect students to infer that something in the image represents something it
        doesn't look like
        - Consider the grade level and adjust complexity accordingly
        - Make images clear, engaging, and educationally purposeful
        - Ensure images support the learning objectives of your content
        - Use color and visual elements thoughtfully to enhance understanding
        - Wait to actually create an image until you have designed ALL other content you need""")
    
    # Shared content that comes after image guidelines
    SHARED_PROMPT_ENDING = textwrap.dedent("""
        When embedding images in Markdown, always use the full, unedited image URL (though you
        should remove a trailing query parameter if present), and include a title and alt text.
        Example if the URL is https://example.com/image.png?token=abc123:
        ```
        ![alt text](https://example.com/image.png "image title")
        ```

        BE CAREFUL NOT TO ALTER THE IMAGE URL BETWEEN THE HTTPS:// AND THE IMAGE FILENAME,
        INCLUSIVE! Altering that portion of the URL will cause the image to not be displayed.
        Verify the URL you are placing into the final content is live, valid URL and is
        EXACTLY the URL you intended to use. If the URL is not live, correct it to be the URL
        you intended to use.
        
        DO NOT give away the answer to a question in the alt text or title of an image.
        
        ## VIDEO EMBEDDING
        
        When you generate videos (such as Manim animations), embed them directly in the content
        using HTML video tags, NOT download links. 
        
        **CRITICAL: Place the video tag directly in markdown - NOT inside code blocks!**
        
        **CORRECT video embedding format (directly in markdown):**
        <video width="800" height="600" controls>
          <source src="https://example.com/video.mp4" type="video/mp4">
          Your browser does not support the video tag.
        </video>
        
        **INCORRECT - Do NOT wrap in code blocks:**
        ```html
        <video width="800" height="600" controls>
          <source src="https://example.com/video.mp4" type="video/mp4">
          Your browser does not support the video tag.
        </video>
        ```
        
        **ALSO INCORRECT - Do NOT use download links:**
        ```
        [Download / View the video](https://example.com/video.mp4)
        ```
        
        **Video embedding guidelines:**
        - Place the HTML <video> tag directly in the markdown content (no code blocks!)
        - Include `controls` attribute so users can play/pause
        - Set reasonable width/height (suggest 800x600 or smaller for readability)
        - Use the full video URL from the tool response
        - Include fallback text for unsupported browsers
        - The video will render inline and be playable directly in the content

        ## WRITING STYLE
        
        All content should be written for a typical student of the appropriate grade in diction,
        sentence structure, style, etc. Do not use words, sentence structures, concepts, or other
        components that a typical grade-level student would not be readily able to understand.
        
        Do not include empty space (e.g., "\\n") or a blank (e.g., "________") for students to fill
        in an answer. A place to enter their answer will be provided by the application sharing the
        content with the student. Students do not have a way to directly interact with the content
        you are creating.
        
        ## LaTeX FORMATTING
        
        ALWAYS follow the MANDATORY LaTeX DELIMITER RULE:
        
        **MANDATORY LaTeX DELIMITER RULE: Use $ ... $ (inline) or $$ ... $$ (display) LaTeX
        delimiters ONLY.**
        
        NEVER include LaTeX in your response without these delimiters.
        
        NEVER use any other LaTeX delimiters. Using brackets [] or parentheses () can create valid
        LaTeX in other contexts, but in markdown, it DOES NOT create a valid LaTeX expression! **A
        SINGLE occurrence of incorrectly delimited LaTeX will cause the entire response to be
        rejected. DO NOT MAKE THIS MISTAKE!**
        
        Format LaTeX operators (e.g., times, div, frac, etc.) using a single, unescaped backslash
        (\\) character.
        
        Proper usage of dollar-sign delimiters around LaTeX is CRITICAL and you MUST ALWAYS be sure
        to do it WHENEVER you use LaTeX!!!
        
        ## GETTING STARTED
        
        Plan out what you are going to do, record that plan, emphasizing how you are using learning 
        science to craft top-quality educational content. Make sure to identify any images you need
        to create, and note that you need to stylize them if appropriate. 
        
        Then proceed through your plan step-by-step. After creating your content, you MUST 
        follow the Content Quality Assurance Workflow described below (STEP 1: LaTeX fix if 
        needed, STEP 2: QC check, STEP 3: iterate if QC fails). 
        
        Only after passing QC should you assess the content against the Question Quality 
        Checklist (if you created questions) and make any final refinements. 
        
        Format your final response as a markdown string - don't use HTML tags (e.g., <br>) or 
        special characters (e.g., '\\n') when markdown can be used instead. Do not place your 
        output in a code block; just output the markdown.""")
    
    # Quality assurance workflow instructions that must be followed for all content
    QA_WORKFLOW_INSTRUCTIONS = textwrap.dedent("""
        ## CONTENT QUALITY ASSURANCE WORKFLOW: CRITICAL - NEVER SKIP THESE STEPS!!!

        Before returning ANY final content, you MUST follow this quality assurance workflow:

        **STEP 1 - LaTeX Delimiter Fix (if applicable):**
        - If your content contains ANY LaTeX expressions (mathematical notation, equations, 
          formulas, etc.), you MUST call the fix_latex_delimiters tool with your complete content.
        - This tool ensures all LaTeX uses proper $ ... $ (inline) or $$ ... $$ (display) 
          delimiters.
        - Use the corrected content returned by this tool for all subsequent steps.
        - If your content has no LaTeX whatsoever, skip directly to Step 2.

        **STEP 2 - Quality Check - MANDATORY FOR ALL CONTENT!!!:**
        - You MUST call the check_content_quality tool with your complete final content.
        - This tool renders your content as students will see it and checks for quality issues.
        - NEVER skip this step - it is REQUIRED for ALL content you create, regardless of how 
          confident you are.

        **STEP 3 - Handle Quality Check Results:**
        IF QC PASSES:
        - Your content is ready! Proceed to return it as your final response.
        
        IF QC FAILS:
        - Carefully read ALL feedback provided by the QC tool
        - Identify the specific blocking issues mentioned
        - Revise your content to thoroughly address EVERY issue raised
        - Return to STEP 1 (run LaTeX fix again if your content contains LaTeX)
        - Continue iterating until QC passes

        **STEP 4 - Iteration Guidelines:**
        - You MUST make AT LEAST 2 complete revision attempts if QC fails
        - After 2 failed attempts, continue iterating if you have clear ideas for fixing the issues
        - Only give up if you are completely out of actionable ideas
        - If you must give up after exhausting all options, return an error message in this exact 
          format:
          "Unable to generate content of sufficient quality after multiple attempts. Final issues: 
          [brief summary of remaining problems]"
        - Think carefully about each QC failure - the feedback is there to help you improve

        **STEP 5 - Return Final Content:**
        - Only after QC PASSES should you return your content
        - Simply return the content itself - do NOT mention that you ran QC checks
        - Do NOT include any meta-commentary about the QC process
        - The QC workflow should be completely invisible to the end user

        **CRITICAL REMINDERS:**
        - LaTeX fix MUST run before QC (if LaTeX is present)
        - QC MUST ALWAYS run before returning ANY final content
        - Failed QC requires revision and re-checking - never return content that failed QC
        - Use QC feedback constructively - it's like having an expert reviewer helping you
        - If images have issues, regenerate them with corrected parameters
        - Pay special attention to text-image mismatches and LaTeX rendering issues

        **Example Workflow:**
        1. Create initial content with images and LaTeX
        2. Call fix_latex_delimiters(content) → get corrected_content
        3. Call check_content_quality(corrected_content) → FAILED: "Image shows 5 items but text 
           says 7"
        4. Revise: Fix text to match image (or regenerate image)
        5. Call fix_latex_delimiters(revised_content) → get corrected_revised_content
        6. Call check_content_quality(corrected_revised_content) → PASSED
        7. Return final content to user
        """)

    def __init__(
        self, *, 
        model: str = "o3", 
        on_event: Callable[[str, Any], None] = None, 
        conversation_id: str | None = None, 
        user_id: str = None, 
        amq_json_format: bool = False, 
        request_id: str = None, 
        use_coach_bot_tools: bool = False,
        cancellation_flag = None
    ) -> None:
        # Construct the system prompt based on tool type
        if use_coach_bot_tools:
            image_guidelines = self.COACHBOT_TOOLS_IMAGE_GUIDELINES
            files = [
                get_file_entry(QUESTION_DESIGN_FILE_KEY),
                get_file_entry(MATH_FIGURES_FILE_KEY),
                # get_file_entry(ACCURATE_FIGURES_FILE_KEY),
                get_file_entry(TEACHING_CONCEPTS_FILE_KEY),
                # get_file_entry(REAL_WORLD_COMPONENTS_FILE_KEY),
                # get_file_entry(CREATING_QUIZZES_FILE_KEY),
                get_file_entry(QUESTION_QUALITY_CHECKLIST_FILE_KEY),
            ]
        else:
            image_guidelines = self.STANDARD_TOOLS_IMAGE_GUIDELINES
            files = [
                get_file_entry(QUESTION_DESIGN_FILE_KEY),
                get_file_entry(MATH_FIGURES_FILE_KEY),
                # get_file_entry(ACCURATE_FIGURES_FILE_KEY),
                get_file_entry(TEACHING_CONCEPTS_FILE_KEY),
                get_file_entry(REAL_WORLD_COMPONENTS_FILE_KEY),
                get_file_entry(CREATING_QUIZZES_FILE_KEY),
                get_file_entry(QUESTION_QUALITY_CHECKLIST_FILE_KEY),
            ]
        
        system_prompt = (
            self.SHARED_SYSTEM_PROMPT_CONTENT + 
            image_guidelines + 
            self.SHARED_PROMPT_ENDING +
            self.QA_WORKFLOW_INSTRUCTIONS
        )

        super().__init__(
            model=model, 
            system_prompt=system_prompt, 
            files=files, 
            on_event=on_event,
            conversation_id=conversation_id, 
            user_id=user_id, 
            amq_json_format=amq_json_format,
            request_id=request_id, 
            effort="high", 
            is_incept=True,
            cancellation_flag=cancellation_flag
        )
        
        # UNIVERSAL TOOLS
        # Add curriculum search tool
        self.add_tool(*search_curriculum_tool())

        # Add batch random generation tool
        self.add_tool(*generate_random_batch_tool())

        # Add LaTeX delimiter fix tool (must run before QC if LaTeX is present)
        self.add_tool(*generate_latex_delimiter_fix_tool())

        # Add simple content QC tool (must run for all content before returning)
        self.add_tool(*generate_simple_content_qc_tool())

        # STANDARD TOOLS
        if not use_coach_bot_tools:
          print("Using standard tools")
          # from edu_agents.tools.html_animation_gen import generate_animation_tool
          from edu_agents.tools.clock_gen import generate_clock_image_tool

          # from edu_agents.tools.svg_shape_gen import generate_svg_shape_tool
          # from edu_agents.tools.image_stylize import stylize_image_tool
          # from edu_agents.tools.gemini_image_gen import generate_image_gemini_tool
          # from edu_agents.tools.image_gen import generate_image_tool
          # from edu_agents.tools.image_quality_checker_ensemble import (
          #     generate_image_quality_checker_ensemble_tool,
          # )
          # from edu_agents.tools.image_quality_checker_gemini import (
          #     generate_image_quality_checker_tool_gemini,
          # )
          # from edu_agents.tools.image_quality_checker_gpt import (
          #     generate_image_quality_checker_gpt_tool,
          # )
          # from edu_agents.tools.image_quality_checker_two_step import (
          #     generate_image_quality_checker_two_step_tool,
          # )
          # from edu_agents.tools.imagen_image_gen import generate_image_imagen_tool
          # from edu_agents.tools.image_quality_checker_claude import (
          #     generate_image_quality_checker_tool_claude,
          # )

          # from edu_agents.tools.circle_gen import generate_circle_image_tool
          # from edu_agents.tools.reve_image_gen import generate_image_reve_tool
          # from edu_agents.tools.svg_image_gen import generate_svg_image_tool
          from edu_agents.tools.intersecting_lines_gen import generate_intersecting_lines_image_tool
          from edu_agents.tools.latex_equation_gen import generate_latex_equation_image_tool
          from edu_agents.tools.manim_animation_gen import generate_manim_animation_tool
          from edu_agents.tools.number_line import generate_number_line_tool
          from edu_agents.tools.ruler_gen import generate_ruler_image_tool
          from edu_agents.tools.shape_2d_gen import generate_2d_shape_image_tool
          from edu_agents.tools.shape_3d_gen import generate_3d_shape_image_tool
          from edu_agents.tools.simple_bar import generate_simple_bar_tool
          from edu_agents.tools.simple_box import generate_simple_box_tool
          from edu_agents.tools.simple_heatmap import generate_simple_heatmap_tool
          from edu_agents.tools.simple_histogram import generate_simple_histogram_tool
          from edu_agents.tools.simple_line import generate_simple_line_tool
          from edu_agents.tools.simple_pie import generate_simple_pie_tool
          from edu_agents.tools.simple_scatter import generate_simple_scatter_tool
          # from edu_agents.tools.svg_sketch_image_gen import generate_svg_sketch_image_tool

          # Add individual matplotlib chart generation tools
          self.add_tool(*generate_simple_bar_tool())
          self.add_tool(*generate_simple_box_tool())
          self.add_tool(*generate_simple_heatmap_tool())
          self.add_tool(*generate_simple_histogram_tool())
          self.add_tool(*generate_simple_line_tool())
          self.add_tool(*generate_simple_pie_tool())
          self.add_tool(*generate_simple_scatter_tool())

          # Add standard clock image generation tool (kept for backward compatibility)
          self.add_tool(*generate_clock_image_tool())

          # Add ruler image generation tool
          self.add_tool(*generate_simple_scatter_tool())
        
          # Add standard clock image generation tool (kept for backward compatibility)
          self.add_tool(*generate_clock_image_tool())
        
          # Add ruler image generation tool
          self.add_tool(*generate_ruler_image_tool())

          # Add number line generation tool
          self.add_tool(*generate_number_line_tool())

          # Add intersecting lines generation tool
          self.add_tool(*generate_intersecting_lines_image_tool())

          # Add LaTeX equation generation tool
          self.add_tool(*generate_latex_equation_image_tool())

          # Add 3D shape generation tool
          self.add_tool(*generate_3d_shape_image_tool())

          # Add LaTeX equation generation tool
          self.add_tool(*generate_latex_equation_image_tool())

          # Add 3D shape generation tool
          self.add_tool(*generate_3d_shape_image_tool())

          # Add 2D shape generation tool
          self.add_tool(*generate_2d_shape_image_tool())

          # Add HTML animation generation tool
        #   self.add_tool(*generate_animation_tool())

          # Add Manim animation generation tool
          self.add_tool(*generate_manim_animation_tool())

          # Add image generation tool
          # self.add_tool(*generate_image_tool())

          # Add SVG image generation tool
          # self.add_tool(*generate_svg_image_tool())
        
          # Add image stylization tool
          # self.add_tool(*stylize_image_tool())

          # Add Gemini image generation tool
          # self.add_tool(*generate_image_gemini_tool())

          # Add Imagen image generation tool
          # self.add_tool(*generate_image_imagen_tool())

          # Add SVG shape generation tool
          # self.add_tool(*generate_svg_shape_tool())
          
          # Add Reve image generation tool
          # self.add_tool(*generate_image_reve_tool())

          # Add SVG sketch image generation tool
          # self.add_tool(*generate_svg_sketch_image_tool())

          # Add image quality checker tool - using ensemble for maximum reliability
          # self.add_tool(*generate_image_quality_checker_gpt_tool())
          # self.add_tool(*generate_image_quality_checker_tool_claude())
          # self.add_tool(*generate_image_quality_checker_tool_gemini())
          # self.add_tool(*generate_image_quality_checker_ensemble_tool())
          # self.add_tool(*generate_image_quality_checker_two_step_tool())

        # COACH-BOT ENHANCED TOOLS
        else:
          print("Using coach-bot enhanced tools")
          # Import coach-bot tools only when needed
          from edu_agents.tools.coach_bot_tools.angles_gen import (
              generate_coach_bot_fractional_angle_image_tool,
              generate_coach_bot_multiple_angles_image_tool,
              generate_coach_bot_single_angle_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.angles_on_circle_gen import (
              generate_coach_bot_angles_on_circle_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.area_models_gen import (
              generate_coach_bot_area_model_image_tool,
              generate_coach_bot_unit_square_decomposition_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.bar_models_gen import (
              generate_coach_bot_comparison_bar_models_image_tool,
              generate_coach_bot_single_bar_model_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.base_ten_blocks_gen import (
              generate_coach_bot_base_ten_blocks_grid_image_tool,
              generate_coach_bot_base_ten_blocks_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.box_plots_gen import (
              generate_coach_bot_box_plots_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.categorical_graphs_gen import (
              generate_coach_bot_categorical_graph_image_tool,
              generate_coach_bot_multi_bar_graph_image_tool,
              generate_coach_bot_multi_picture_graph_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.clock_gen import generate_coach_bot_clock_image_tool
          from edu_agents.tools.coach_bot_tools.combo_points_table_graph_gen import (
              generate_coach_bot_combo_points_table_graph_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.coordinate_graphing_gen import (
              generate_coach_bot_coordinate_points_image_tool,
              generate_coach_bot_coordinate_points_with_context_image_tool,
              generate_coach_bot_scatter_plot_image_tool,
              generate_coach_bot_stats_scatter_plot_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.counting_gen import (
              generate_coach_bot_counting_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.data_table_with_graph_gen import (
              generate_coach_bot_data_table_with_graph_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.decimal_grid_gen import (
              generate_coach_bot_decimal_comparison_image_tool,
              generate_coach_bot_decimal_grid_image_tool,
              generate_coach_bot_decimal_multiplication_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.divide_into_equal_groups_gen import (
              generate_coach_bot_divide_into_equal_groups_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.divide_items_into_array_gen import (
              generate_coach_bot_divide_items_into_array_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.equation_tape_diagram_gen import (
              generate_coach_bot_equation_tape_diagram_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.flow_chart_gen import (
              generate_coach_bot_flowchart_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.fraction_models_gen import (
              generate_coach_bot_divided_shapes_image_tool,
              generate_coach_bot_fraction_models_image_tool,
              generate_coach_bot_fraction_multiplication_units_image_tool,
              generate_coach_bot_fraction_pairs_image_tool,
              generate_coach_bot_fraction_strips_image_tool,
              generate_coach_bot_mixed_fractions_image_tool,
              generate_coach_bot_unequal_fractions_image_tool,
              generate_coach_bot_whole_fractions_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.geometric_shapes_3d_gen import (
              generate_coach_bot_3d_objects_image_tool,
              generate_coach_bot_cross_section_image_tool,
              generate_coach_bot_right_prisms_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.geometric_shapes_gen import (
              generate_coach_bot_geometric_shapes_image_tool,
              generate_coach_bot_shape_with_right_angles_image_tool,
              generate_coach_bot_shapes_with_angles_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.graphing_function_gen import (
              generate_coach_bot_circle_function_image_tool,
              generate_coach_bot_cubic_function_image_tool,
              generate_coach_bot_cubic_function_quadrant_one_image_tool,
              generate_coach_bot_ellipse_function_image_tool,
              generate_coach_bot_exponential_function_image_tool,
              generate_coach_bot_exponential_function_quadrant_one_image_tool,
              generate_coach_bot_hyperbola_function_image_tool,
              generate_coach_bot_linear_function_image_tool,
              generate_coach_bot_linear_function_quadrant_one_image_tool,
              generate_coach_bot_quadratic_function_image_tool,
              generate_coach_bot_quadratic_function_quadrant_one_image_tool,
              generate_coach_bot_rational_function_image_tool,
              generate_coach_bot_rational_function_quadrant_one_image_tool,
              generate_coach_bot_sideways_parabola_function_image_tool,
              generate_coach_bot_square_root_function_image_tool,
              generate_coach_bot_square_root_function_quadrant_one_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.histogram_gen import (
              generate_coach_bot_histogram_image_tool,
              generate_coach_bot_histogram_pair_image_tool,
              generate_coach_bot_histogram_with_dotted_bin_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.line_graph_gen import (
              generate_coach_bot_line_graph_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.line_plots_gen import (
              generate_coach_bot_double_line_plot_image_tool,
              generate_coach_bot_single_line_plot_image_tool,
              generate_coach_bot_stacked_line_plots_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.lines_of_best_fit_gen import (
              generate_coach_bot_lines_of_best_fit_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.measurement_comparison_gen import (
              generate_coach_bot_measurement_comparison_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.measurements_gen import (
              generate_coach_bot_measurement_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.number_line_clock_gen import (
              generate_coach_bot_number_line_clock_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.number_lines_gen import (
              generate_coach_bot_decimal_comparison_number_line_image_tool,
              generate_coach_bot_extended_unit_fraction_number_line_image_tool,
              generate_coach_bot_fixed_step_number_line_image_tool,
              generate_coach_bot_number_line_image_tool,
              generate_coach_bot_unit_fraction_number_line_image_tool,
              generate_coach_bot_vertical_number_line_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.object_array_gen import (
              generate_coach_bot_object_array_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.pedigree_chart_gen import (
              generate_coach_bot_pedigree_chart_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.piecewise_graphing_gen import (
              generate_coach_bot_piecewise_function_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.polygon_scales_gen import (
              generate_coach_bot_polygon_scale_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.prism_nets_gen import (
              generate_coach_bot_cube_net_image_tool,
              generate_coach_bot_dual_prism_nets_image_tool,
              generate_coach_bot_rectangular_prism_net_image_tool,
              generate_coach_bot_rectangular_pyramid_net_image_tool,
              generate_coach_bot_square_pyramid_net_image_tool,
              generate_coach_bot_triangular_prism_net_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.protractor_gen import (
              generate_coach_bot_protractor_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.ratio_object_array_gen import (
              generate_coach_bot_ratio_object_array_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.rectangular_prisms_gen import (
              generate_coach_bot_base_area_prisms_image_tool,
              generate_coach_bot_rectangular_prisms_image_tool,
              generate_coach_bot_unit_cube_figure_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.rulers_gen import (
              generate_coach_bot_ruler_measurement_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.shapes_decomposition_gen import (
              generate_coach_bot_compound_area_figure_image_tool,
              generate_coach_bot_rhombus_diagonals_image_tool,
              generate_coach_bot_shape_decomposition_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.spinners_gen import (
              generate_coach_bot_spinner_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.stepwise_patterns_gen import (
              generate_coach_bot_stepwise_pattern_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.symmetry_gen import (
              generate_coach_bot_lines_of_symmetry_image_tool,
              generate_coach_bot_symmetry_identification_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.table_scatterplots_gen import (
              generate_coach_bot_table_and_scatterplots_image_tool,
          )
          from edu_agents.tools.coach_bot_tools.table_tools_gen import (
              generate_coach_bot_data_table_image_tool,
              generate_coach_bot_probability_table_image_tool,
              generate_coach_bot_simple_table_image_tool,
              generate_coach_bot_table_group_image_tool,
              generate_coach_bot_two_way_table_image_tool,
          )

          # Coach-bot style clock image generation tool
          self.add_tool(*generate_coach_bot_clock_image_tool())
          
          # Coach-bot style angles tools
          self.add_tool(*generate_coach_bot_angles_on_circle_image_tool())
          self.add_tool(*generate_coach_bot_single_angle_image_tool())
          self.add_tool(*generate_coach_bot_multiple_angles_image_tool())
          self.add_tool(*generate_coach_bot_fractional_angle_image_tool())
          
          # Coach-bot style area model tools
          self.add_tool(*generate_coach_bot_area_model_image_tool())
          self.add_tool(*generate_coach_bot_unit_square_decomposition_image_tool())
          
          # Coach-bot style bar model tools
          self.add_tool(*generate_coach_bot_single_bar_model_image_tool())
          self.add_tool(*generate_coach_bot_comparison_bar_models_image_tool())
          
          # Coach-bot style base ten blocks tools
          self.add_tool(*generate_coach_bot_base_ten_blocks_image_tool())
          self.add_tool(*generate_coach_bot_base_ten_blocks_grid_image_tool())
          
          # Coach-bot style box plots tool
          self.add_tool(*generate_coach_bot_box_plots_image_tool())
          
          # Coach-bot style categorical graphs tools
          self.add_tool(*generate_coach_bot_categorical_graph_image_tool())
          self.add_tool(*generate_coach_bot_multi_bar_graph_image_tool())
          self.add_tool(*generate_coach_bot_multi_picture_graph_image_tool())
          
          # Coach-bot style combo points table graph tool
          self.add_tool(*generate_coach_bot_combo_points_table_graph_image_tool())
          
          # Coach-bot style counting tool
          self.add_tool(*generate_coach_bot_counting_image_tool())
          
          # Coach-bot style data table with graph tool
          self.add_tool(*generate_coach_bot_data_table_with_graph_image_tool())
          
          # Coach-bot style decimal grid tools
          self.add_tool(*generate_coach_bot_decimal_grid_image_tool())
          self.add_tool(*generate_coach_bot_decimal_comparison_image_tool())
          self.add_tool(*generate_coach_bot_decimal_multiplication_image_tool())
          
          # Coach-bot style grouping and array tools
          self.add_tool(*generate_coach_bot_divide_into_equal_groups_image_tool())
          self.add_tool(*generate_coach_bot_divide_items_into_array_image_tool())
          
          # Coach-bot style equation tape diagram tool
          self.add_tool(*generate_coach_bot_equation_tape_diagram_image_tool())
          
          # Coach-bot style flowchart tool
          self.add_tool(*generate_coach_bot_flowchart_image_tool())
          
          # Coach-bot style fraction model tools
          self.add_tool(*generate_coach_bot_fraction_models_image_tool())
          self.add_tool(*generate_coach_bot_fraction_pairs_image_tool())
          self.add_tool(*generate_coach_bot_fraction_multiplication_units_image_tool())
          self.add_tool(*generate_coach_bot_divided_shapes_image_tool())
          self.add_tool(*generate_coach_bot_unequal_fractions_image_tool())
          self.add_tool(*generate_coach_bot_mixed_fractions_image_tool())
          self.add_tool(*generate_coach_bot_whole_fractions_image_tool())
          self.add_tool(*generate_coach_bot_fraction_strips_image_tool())
          
          # Coach-bot style 3D geometry tools
          self.add_tool(*generate_coach_bot_3d_objects_image_tool())
          self.add_tool(*generate_coach_bot_cross_section_image_tool())
          self.add_tool(*generate_coach_bot_right_prisms_image_tool())
          
          # Coach-bot style 2D geometry tools
          self.add_tool(*generate_coach_bot_geometric_shapes_image_tool())
          self.add_tool(*generate_coach_bot_shapes_with_angles_image_tool())
          self.add_tool(*generate_coach_bot_shape_with_right_angles_image_tool())
          
          # Coach-bot style graphing function tools - Full coordinate plane
          self.add_tool(*generate_coach_bot_linear_function_image_tool())
          self.add_tool(*generate_coach_bot_quadratic_function_image_tool())
          self.add_tool(*generate_coach_bot_exponential_function_image_tool())
          self.add_tool(*generate_coach_bot_cubic_function_image_tool())
          self.add_tool(*generate_coach_bot_square_root_function_image_tool())
          self.add_tool(*generate_coach_bot_rational_function_image_tool())
          self.add_tool(*generate_coach_bot_circle_function_image_tool())
          self.add_tool(*generate_coach_bot_sideways_parabola_function_image_tool())
          self.add_tool(*generate_coach_bot_hyperbola_function_image_tool())
          self.add_tool(*generate_coach_bot_ellipse_function_image_tool())
          
          # Coach-bot style graphing function tools - Quadrant I only  
          self.add_tool(*generate_coach_bot_linear_function_quadrant_one_image_tool())
          self.add_tool(*generate_coach_bot_quadratic_function_quadrant_one_image_tool())
          self.add_tool(*generate_coach_bot_exponential_function_quadrant_one_image_tool())
          self.add_tool(*generate_coach_bot_cubic_function_quadrant_one_image_tool())
          self.add_tool(*generate_coach_bot_square_root_function_quadrant_one_image_tool())
          self.add_tool(*generate_coach_bot_rational_function_quadrant_one_image_tool())
          
          # Coach-bot style piecewise function tools
          self.add_tool(*generate_coach_bot_piecewise_function_image_tool())

          # Coach-bot style coordinate graphing tools
          self.add_tool(*generate_coach_bot_coordinate_points_image_tool())
          self.add_tool(*generate_coach_bot_coordinate_points_with_context_image_tool())
          self.add_tool(*generate_coach_bot_scatter_plot_image_tool())
          self.add_tool(*generate_coach_bot_stats_scatter_plot_image_tool())
          
          # Coach-bot style histogram tools
          self.add_tool(*generate_coach_bot_histogram_image_tool())
          self.add_tool(*generate_coach_bot_histogram_pair_image_tool())
          self.add_tool(*generate_coach_bot_histogram_with_dotted_bin_image_tool())
          
          # Coach-bot style line plot tools
          self.add_tool(*generate_coach_bot_single_line_plot_image_tool())
          self.add_tool(*generate_coach_bot_stacked_line_plots_image_tool())
          self.add_tool(*generate_coach_bot_double_line_plot_image_tool())
          
          # Coach-bot style lines of best fit tools
          self.add_tool(*generate_coach_bot_lines_of_best_fit_image_tool())
          
          # Coach-bot style line graph tools
          self.add_tool(*generate_coach_bot_line_graph_image_tool())
          
          # Coach-bot style measurement tools
          self.add_tool(*generate_coach_bot_measurement_comparison_image_tool())
          self.add_tool(*generate_coach_bot_measurement_image_tool())
          
          # Coach-bot style number line tools
          self.add_tool(*generate_coach_bot_number_line_clock_image_tool())
          self.add_tool(*generate_coach_bot_number_line_image_tool())
          self.add_tool(*generate_coach_bot_fixed_step_number_line_image_tool())
          self.add_tool(*generate_coach_bot_unit_fraction_number_line_image_tool())
          self.add_tool(*generate_coach_bot_extended_unit_fraction_number_line_image_tool())
          self.add_tool(*generate_coach_bot_decimal_comparison_number_line_image_tool())
          self.add_tool(*generate_coach_bot_vertical_number_line_image_tool())
          
          # Coach-bot style object array tools
          self.add_tool(*generate_coach_bot_object_array_image_tool())
          
          # Coach-bot style protractor tools
          self.add_tool(*generate_coach_bot_protractor_image_tool())
          
          # Coach-bot style polygon scale tools
          self.add_tool(*generate_coach_bot_polygon_scale_image_tool())
          
          # Coach-bot style pedigree chart tools
          self.add_tool(*generate_coach_bot_pedigree_chart_image_tool())
          
          # Coach-bot style 3D prism net tools
          self.add_tool(*generate_coach_bot_rectangular_prism_net_image_tool())
          self.add_tool(*generate_coach_bot_cube_net_image_tool())
          self.add_tool(*generate_coach_bot_triangular_prism_net_image_tool())
          self.add_tool(*generate_coach_bot_square_pyramid_net_image_tool())
          self.add_tool(*generate_coach_bot_rectangular_pyramid_net_image_tool())
          self.add_tool(*generate_coach_bot_dual_prism_nets_image_tool())
          
          # Coach-bot style ratio object array tools
          self.add_tool(*generate_coach_bot_ratio_object_array_image_tool())
          
          # Coach-bot style rectangular prisms tools
          self.add_tool(*generate_coach_bot_rectangular_prisms_image_tool())
          self.add_tool(*generate_coach_bot_base_area_prisms_image_tool())
          self.add_tool(*generate_coach_bot_unit_cube_figure_image_tool())
          
          # Coach-bot style ruler measurement tools
          self.add_tool(*generate_coach_bot_ruler_measurement_image_tool())
          
          # Coach-bot style shape decomposition tools
          self.add_tool(*generate_coach_bot_shape_decomposition_image_tool())
          self.add_tool(*generate_coach_bot_compound_area_figure_image_tool())
          self.add_tool(*generate_coach_bot_rhombus_diagonals_image_tool())
          
          # Coach-bot style spinner tools
          self.add_tool(*generate_coach_bot_spinner_image_tool())
          
          # Coach-bot style stepwise pattern tools
          self.add_tool(*generate_coach_bot_stepwise_pattern_image_tool())
          
          # Coach-bot style symmetry tools
          self.add_tool(*generate_coach_bot_lines_of_symmetry_image_tool())
          self.add_tool(*generate_coach_bot_symmetry_identification_image_tool())
          
          # Coach-bot style table and scatterplots tools
          self.add_tool(*generate_coach_bot_table_and_scatterplots_image_tool())
          
          # Coach-bot style table tools
          self.add_tool(*generate_coach_bot_simple_table_image_tool())
          self.add_tool(*generate_coach_bot_two_way_table_image_tool())
          self.add_tool(*generate_coach_bot_probability_table_image_tool())
          self.add_tool(*generate_coach_bot_data_table_image_tool())
          self.add_tool(*generate_coach_bot_table_group_image_tool())