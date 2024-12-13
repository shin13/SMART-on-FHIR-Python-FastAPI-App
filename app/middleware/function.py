async def extract_observation_data(fhir_json, observation_type):
    """
    Extracts the value and unit from a FHIR Observation resource.

    Args:
        fhir_json (dict): The FHIR JSON resource.
        observation_type (str): The type of observation to extract (e.g., "height", "weight", "bmi").

    Returns:
        str: The extracted observation value and unit, or an error message if the data is not found or invalid.
    """
    # Bundle
    if fhir_json.get("resourceType") == "Bundle" and fhir_json.get("total", 0) > 0:
        try:
            entry = fhir_json["entry"][0]["resource"]
            value = entry.get("valueQuantity", {}).get("value")
            unit = entry.get("valueQuantity", {}).get("unit")

            if value is not None and unit is not None:
                try:
                    result = float(round(value, 1))
                    return f"{result} {unit}"
                except (TypeError, ValueError):
                    return f"{observation_type.capitalize()} data is not a valid number"
            
            return f"Complete {observation_type} data not found"
        
        except (KeyError, IndexError):
            return f"{observation_type.capitalize()} data format is incorrect"

    # Single
    try:
        value = fhir_json.get("valueQuantity", {}).get("value")
        unit = fhir_json.get("valueQuantity", {}).get("unit")
        
        if value is not None and unit is not None:
            try:
                result = float(round(value, 1))
                return f"{result} {unit}"
            except (TypeError, ValueError):
                return f"{observation_type.capitalize()} data is not a valid number"
        
        return f"No {observation_type} data found"
    
    except Exception:
        return f"An unknown error occurred while processing {observation_type} data"
