from requests import get
from requests.exceptions import RequestException
from app.middleware.exception import parse_json_safely

def fetch_observation(uri: str, headers: dict, body: dict) -> dict:
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
        return {"error": f"Request failed: {str(e)}"}
    
    obs_json = parse_json_safely(response)
    
    if obs_json.get("resourceType") not in ["Observation", "Bundle"]:
        return {"error": "No valid observation data were found"}
    
    return obs_json