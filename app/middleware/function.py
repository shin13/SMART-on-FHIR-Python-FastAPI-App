import json
import logging
from typing import Union, Dict, List
from requests import get
from requests.exceptions import RequestException
from app.middleware.exception import exception_message


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
    

def fetch_fhir_json(uri: str, headers: dict, body: dict):
    """
    Fetches observation data from a given FHIR URI.
    
    Args:
        uri (str): The FHIR endpoint URI.
        headers (dict): The headers to be sent with the request.
        body (dict): The request body to be sent with the request.
    
    Returns:
        dict: Parsed observation data or an error message if the data is invalid.
    """
    try:
        response = get(uri, headers=headers, data=body, timeout=10)
        response.raise_for_status()
    except RequestException as e:
        return {"error": f"Request failed: {exception_message(e)}"}
    
    fhir_json = parse_json_safely(response)
    
    if fhir_json["resourceType"] == "OperationOutcome":
        raise ValueError(
            """
            The patient you selected does not have requested data available.
            """
        )
    
    if fhir_json.get("resourceType") not in ["Observation", "Bundle"]:
        return {"error": "No valid FHIR data were found"}
    
    return fhir_json