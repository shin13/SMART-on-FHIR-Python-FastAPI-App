import json
import logging
from typing import Union, Dict, List


def exception_message(e):
    return f"Exception[{type(e).__name__}] occurred. Details: {str(e)}"


class JSONParseError(Exception):
    """Custom exception for JSON parsing errors."""
    pass

def parse_json_safely(data) -> Union[Dict, List]:
    """
    Safely parse JSON data and handle potential errors.
    
    Args:
    data: The data to be parsed as JSON.
    logger: A logging.Logger instance for error logging.
    
    Returns:
    Parsed JSON data.
    
    Raises:
    JSONParseError: If JSON parsing fails.
    """
    system_logger = logging.getLogger('custom.error')

    try:
        return json.loads(data) if isinstance(data, str) else data.json()
    except json.JSONDecodeError as e:
        system_logger.error("JSON parsing error: Unable to parse resource")
        raise JSONParseError("Data is not in valid JSON format. Maybe the permissions are set incorrectly or the app isn't registered correctly. Data not returned in JSON format. You probably haven't set the correct scope permissions, or registered the app with the EHR vendor so that it has access to this resource in Read or Search mode.") from e