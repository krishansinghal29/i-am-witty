"""Convert between v1 (string) and v2 (array) question formats.

Ported from the legacy backend so evaluator prompts can render any supported
question payload as plain text. Uses the stdlib logger instead of the old
project logger.
"""

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


def convert_question_to_string(question: Any) -> str:
    """
    Convert a question from any format (v1 string or v2 array) to a string format.

    Args:
        question: Can be:
            - String (v1 format): "Question text"
            - Array (v2 format): [{"role": "She", "content": "Question text"}]
            - Dict with question key: {"question": "..." or [...]}
            - JSON string of above formats

    Returns:
        str: Question content as a simple string
    """
    try:
        # If it's already a string and doesn't look like JSON, return as-is
        if isinstance(question, str):
            # Try to parse as JSON first
            try:
                parsed = json.loads(question)
                return convert_question_to_string(parsed)
            except (json.JSONDecodeError, TypeError):
                # Not JSON, return as-is
                return question

        # If it's a dict, check if it has a 'question' key
        if isinstance(question, dict):
            if 'question' in question:
                return convert_question_to_string(question['question'])
            else:
                # If it's a dict but no 'question' key, convert to string
                return str(question)

        # If it's a list (v2 format), extract content from all items
        if isinstance(question, list):
            contents = []
            for item in question:
                if isinstance(item, dict) and 'content' in item:
                    # Add role prefix if available for context
                    role = item.get('role', '')
                    content = item.get('content', '')
                    if role:
                        contents.append(f"{role}: {content}")
                    else:
                        contents.append(content)
                elif isinstance(item, dict):
                    # Dict without content key, convert to string
                    contents.append(str(item))
                else:
                    # Other types, convert to string
                    contents.append(str(item))

            return '\n'.join(contents) if contents else ''

        # For any other type, convert to string
        return str(question)

    except Exception as e:
        logger.warning(f"Error converting question to string: {str(e)}, returning raw string conversion")
        return str(question)
