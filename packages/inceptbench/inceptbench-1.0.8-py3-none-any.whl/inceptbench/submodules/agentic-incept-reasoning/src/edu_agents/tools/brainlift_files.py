"""Module defining file IDs of supporting documents stored in OpenAI Files.

Instead of hard-coding the `file_id`s, we now load them from the Supabase table
`incept_files` which has the following schema:

    file_key   | varchar  | (e.g. "CURRICULUM_FILE")
    file_id    | varchar  | (e.g. "file-xxxxxxxxxxxxxxxx")

The table must already be populated (see screenshot in the task discussion).
"""

from __future__ import annotations

from typing import Dict

from utils.supabase_utils import query_supabase_table

CURRICULUM_FILE_KEY = "CURRICULUM_FILE"
DEPTH_OF_KNOWLEDGE_FILE_KEY = "DEPTH_OF_KNOWLEDGE_FILE"
DIFFICULTY_FILE_KEY = "DIFFICULTY_FILE"
WHAT_MAKES_A_GOOD_QUESTION_FILE_KEY = "WHAT_MAKES_A_GOOD_QUESTION_FILE"
WHAT_MAKES_A_GREAT_QUIZ_FILE_KEY = "WHAT_MAKES_A_GREAT_QUIZ_FILE"
QUESTION_DESIGN_FILE_KEY = "QUESTION_DESIGN_FILE"
ACCURATE_FIGURES_FILE_KEY = "ACCURATE_FIGURES_FILE"
GENERAL_IMAGES_FILE_KEY = "GENERAL_IMAGES_FILE"
STYLIZING_IMAGES_FILE_KEY = "STYLIZING_IMAGES_FILE"
MATH_FIGURES_FILE_KEY = "MATH_FIGURES_FILE"
CREATING_QUIZZES_FILE_KEY = "CREATING_QUIZZES_FILE"
TEACHING_CONCEPTS_FILE_KEY = "TEACHING_CONCEPTS_FILE"
REAL_WORLD_COMPONENTS_FILE_KEY = "REAL_WORLD_COMPONENTS_FILE"
QUESTION_QUALITY_CHECKLIST_FILE_KEY = "QUESTION_QUALITY_CHECKLIST_FILE"

def get_file_entry(key: str) -> Dict[str, str]:
    """Fetch a single `file_id` for `key` and return the dict expected by OpenAI."""
    def _load_file_map() -> Dict[str, str]:
        """Load {file_key: file_id} mapping from the `incept_files` table."""
        rows = query_supabase_table("incept_files", "file_key,file_id")
        return {row["file_key"]: row["file_id"] for row in rows}

    file_map = _load_file_map()
    try:
        file_id = file_map[key]
    except KeyError as exc:
        raise KeyError(
            f"File key '{key}' not found in Supabase table 'incept_files'."
        ) from exc

    return {"type": "input_file", "file_id": file_id}