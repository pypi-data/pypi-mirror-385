import openai

CLASSIFY_SCENARIO_PROMPT = """You are a helpful assistant that classifies user requests
into scenarios. The scenarios are:
- "multiple-choice question"
- "fill-in-the-blank question"
- "quiz"
- "other"

You will be given a user request and you must classify it into one of these categories.
Return ONLY the category name, no other text.
"""

def classify_scenario(scenario: str) -> str:
    client = openai.OpenAI(timeout=60.0)  # 1 minute timeout for classification calls
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": CLASSIFY_SCENARIO_PROMPT},
            {"role": "user", "content": scenario}
        ],
    )
    return response.choices[0].message.content

def is_multiple_choice_question(scenario: str) -> bool:
    return classify_scenario(scenario) == "multiple-choice question"

def is_fill_in_the_blank_question(scenario: str) -> bool:
    return classify_scenario(scenario) == "fill-in-the-blank question"

def is_quiz(scenario: str) -> bool:
    return classify_scenario(scenario) == "quiz"
