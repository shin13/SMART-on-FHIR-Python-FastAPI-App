import logging

from fastapi import APIRouter, Depends
from oauthlib.oauth2 import WebApplicationClient

from app.configs.config import credentialSettings
from app.middleware.exception import exception_message
from app.middleware.function import fetch_fhir_json


router = APIRouter()
client = WebApplicationClient(credentialSettings.CLIENT_ID)

uvicorn_logger = logging.getLogger('uvicorn.error')
system_logger = logging.getLogger('custom.error')


#### 依賴函數
async def get_height(tokens):

    # Getting data in the way prescribed by OAuthLib package
    uri, headers, body = client.add_token(
        f"{credentialSettings.BASE_URL}/Observation?patient={tokens['patient']}&category=vital-signs&code=8302-2",
        headers={"Accept": "application/fhir+json"},
    )

    try:
        obs_json = fetch_fhir_json(uri, headers, body)
        
        # Bundle
        if obs_json.get("resourceType") == "Bundle" and obs_json.get("total", 0) > 0:
            try:
                entry = obs_json["entry"][0]["resource"]
                value = entry.get("valueQuantity", {}).get("value")
                unit = entry.get("valueQuantity", {}).get("unit")

                if value is not None and unit is not None:
                    try:
                        result = float(round(value, 1))
                        return f"{result} {unit}"
                    except (TypeError, ValueError):
                        return "Height data is not a valid number"
                
                return "Complete height data not found"
            
            except (KeyError, IndexError):
                return "Height data format is incorrect"

        # Single 
        try:
            value = obs_json.get("valueQuantity", {}).get("value")
            unit = obs_json.get("valueQuantity", {}).get("unit")
            
            if value is not None and unit is not None:
                try:
                    result = float(round(value, 1))
                    return f"{result} {unit}"
                except (TypeError, ValueError):
                    return "Height data is not a valid number"
            
            return "No height data found"
        
        except Exception:
            return "An unknown error occurred while processing height data"

    except Exception as e:
        system_logger.error(f"An error occurred while retrieving the height observation resource: {exception_message(e)}")
        raise ValueError(f"Found the following error pulling Observation FHIR resource: {exception_message(e)}") from e


async def get_weight(tokens):

    # Getting data in the way prescribed by OAuthLib package
    uri, headers, body = client.add_token(
        f"{credentialSettings.BASE_URL}/Observation?patient={tokens['patient']}&category=vital-signs&code=29463-7",
        headers={"Accept": "application/fhir+json"},
    )

    try:
        obs_json = fetch_fhir_json(uri, headers, body)

        # Bundle
        if obs_json.get("resourceType") == "Bundle" and obs_json.get("total", 0) > 0:
            try:
                entry = obs_json["entry"][0]["resource"]
                value = entry.get("valueQuantity", {}).get("value")
                unit = entry.get("valueQuantity", {}).get("unit")

                if value is not None and unit is not None:
                    try:
                        result = float(round(value, 1))
                        return f"{result} {unit}"
                    except (TypeError, ValueError):
                        return "Weight data is not a valid number"
                
                return "Complete weight data not found"
            
            except (KeyError, IndexError):
                return "Weight data format is incorrect"

        # Single 
        try:
            value = obs_json.get("valueQuantity", {}).get("value")
            unit = obs_json.get("valueQuantity", {}).get("unit")
            
            if value is not None and unit is not None:
                try:
                    result = float(round(value, 1))
                    return f"{result} {unit}"
                except (TypeError, ValueError):
                    return "Weight data is not a valid number"
            
            return "No weight data were found"
        
        except Exception:
            return "An unknown error occurred while processing weight data"

    except Exception as e:
        system_logger.error(f"An error occurred while retrieving the weight observation resource: {exception_message(e)}")
        raise ValueError(f"Found the following error pulling Observation FHIR resource: {exception_message(e)}") from e


async def get_bmi(tokens):

    # Getting data in the way prescribed by OAuthLib package
    uri, headers, body = client.add_token(
        f"{credentialSettings.BASE_URL}/Observation?patient={tokens['patient']}&category=vital-signs&code=39156-5",
        headers={"Accept": "application/fhir+json"},
    )

    try:
        obs_json = fetch_fhir_json(uri, headers, body)

        # Bundle
        if obs_json.get("resourceType") == "Bundle" and obs_json.get("total", 0) > 0:
            try:
                entry = obs_json["entry"][0]["resource"]
                value = entry.get("valueQuantity", {}).get("value")
                unit = entry.get("valueQuantity", {}).get("unit")

                if value is not None and unit is not None:
                    try:
                        result = float(round(value, 1))
                        return f"{result} {unit}"
                    except (TypeError, ValueError):
                        return "BMI data is not a valid number"
                
                return "Complete BMI data not found"
            
            except (KeyError, IndexError):
                return "BMI data format is incorrect"

        # Single 
        try:
            value = obs_json.get("valueQuantity", {}).get("value")
            unit = obs_json.get("valueQuantity", {}).get("unit")
            
            if value is not None and unit is not None:
                try:
                    result = float(round(value, 1))
                    return f"{result} {unit}"
                except (TypeError, ValueError):
                    return "BMI data is not a valid number"
            
            return "No BMI data were found"
        
        except Exception:
            return "An unknown error occurred while processing BMI data"

    except Exception as e:
        system_logger.error(f"An error occurred while retrieving the BMI observation resource: {exception_message(e)}")
        raise ValueError(f"Found the following error pulling Observation FHIR resource: {exception_message(e)}") from e


async def get_bp(tokens):
    # Getting data in the way prescribed by OAuthLib package
    uri, headers, body = client.add_token(
        f"{credentialSettings.BASE_URL}/Observation?patient={tokens['patient']}&category=vital-signs&code=55284-4",
        headers={"Accept": "application/fhir+json"},
    )

    try:
        obs_json = fetch_fhir_json(uri, headers, body)

        # Bundle
        if obs_json.get("resourceType") == "Bundle" and obs_json.get("total", 0) > 0:
            try:
                entry = obs_json["entry"][0]["resource"]
                components = entry.get("component", [])
                
                if len(components) >= 2:
                    sys_component = components[0]
                    dias_component = components[1]

                    sys_value = sys_component.get("valueQuantity", {}).get("value")
                    sys_unit = sys_component.get("valueQuantity", {}).get("unit")

                    if sys_value is not None and sys_unit is not None:
                        try:
                            sys_bp = f"{float(round(sys_value, 1))} {sys_unit}"
                        except (TypeError, ValueError):
                            sys_bp = "Systolic blood pressure data is not a valid number"
                    else:
                        sys_bp = "Complete systolic blood pressure data not found"

                    dias_value = dias_component.get("valueQuantity", {}).get("value")
                    dias_unit = dias_component.get("valueQuantity", {}).get("unit")

                    if dias_value is not None and dias_unit is not None:
                        try:
                            dias_bp = f"{float(round(dias_value, 1))} {dias_unit}"
                        except (TypeError, ValueError):
                            dias_bp = "Diastolic blood pressure data is not a valid number"
                    else:
                        dias_bp = "Complete diastolic blood pressure data not found"

                    return sys_bp, dias_bp
                
                return "Blood pressure components not found"
            
            except (KeyError, IndexError):
                return "Blood pressure data format is incorrect"

        # Single 
        if obs_json.get("resourceType") == "Observation":
            try:
                components = obs_json.get("component", [])
                
                if len(components) >= 2:
                    sys_component = components[0]
                    dias_component = components[1]

                    sys_value = sys_component.get("valueQuantity", {}).get("value")
                    sys_unit = sys_component.get("valueQuantity", {}).get("unit")

                    if sys_value is not None and sys_unit is not None:
                        try:
                            sys_bp = f"{float(round(sys_value, 1))} {sys_unit}"
                        except (TypeError, ValueError):
                            sys_bp = "Systolic blood pressure data is not a valid number"
                    else:
                        sys_bp = "Complete systolic blood pressure data not found"

                    dias_value = dias_component.get("valueQuantity", {}).get("value")
                    dias_unit = dias_component.get("valueQuantity", {}).get("unit")

                    if dias_value is not None and dias_unit is not None:
                        try:
                            dias_bp = f"{float(round(dias_value, 1))} {dias_unit}"
                        except (TypeError, ValueError):
                            dias_bp = "Diastolic blood pressure data is not a valid number"
                    else:
                        dias_bp = "Complete diastolic blood pressure data not found"

                    return sys_bp, dias_bp
                
                return "Blood pressure components not found"
            
            except Exception:
                return "An unknown error occurred while processing blood pressure data"

        return "No blood pressure data found"
    
    except Exception as e:
        system_logger.error(f"An error occurred while retrieving the blood pressure observation resource: {exception_message(e)}")
        raise ValueError(f"Found the following error pulling Observation FHIR resource: {exception_message(e)}") from e


async def get_hdl(tokens):

    # Getting data in the way prescribed by OAuthLib package
    uri, headers, body = client.add_token(
        f"{credentialSettings.BASE_URL}/Observation?patient={tokens['patient']}&category=laboratory&code=2085-9",
        headers={"Accept": "application/fhir+json"},
    )

    try:
        obs_json = fetch_fhir_json(uri, headers, body)

        # Bundle
        if obs_json.get("resourceType") == "Bundle" and obs_json.get("total", 0) > 0:
            try:
                entry = obs_json["entry"][0]["resource"]
                value = entry.get("valueQuantity", {}).get("value")
                unit = entry.get("valueQuantity", {}).get("unit")

                if value is not None and unit is not None:
                    try:
                        result = float(round(value, 1))
                        return f"{result} {unit}"
                    except (TypeError, ValueError):
                        return "HDL data is not a valid number"
                
                return "Complete HDL data not found"
            
            except (KeyError, IndexError):
                return "HDL data format is incorrect"

        # Single 
        try:
            value = obs_json.get("valueQuantity", {}).get("value")
            unit = obs_json.get("valueQuantity", {}).get("unit")
            
            if value is not None and unit is not None:
                try:
                    result = float(round(value, 1))
                    return f"{result} {unit}"
                except (TypeError, ValueError):
                    return "HDL data is not a valid number"
            
            return "No HDL data were found"
        
        except Exception:
            return "An unknown error occurred while processing HDL data"

    except Exception as e:
        system_logger.error(f"An error occurred while retrieving the HDL observation resource: {exception_message(e)}")
        raise ValueError(f"Found the following error pulling Observation FHIR resource: {exception_message(e)}") from e


async def get_ldl(tokens):
    # Getting data in the way prescribed by OAuthLib package
    uri, headers, body = client.add_token(
        f"{credentialSettings.BASE_URL}/Observation?patient={tokens['patient']}&category=laboratory&code=18262-6",
        headers={"Accept": "application/fhir+json"},
    )

    try:
        obs_json = fetch_fhir_json(uri, headers, body)

        # Bundle
        if obs_json.get("resourceType") == "Bundle" and obs_json.get("total", 0) > 0:
            try:
                entry = obs_json["entry"][0]["resource"]
                value = entry.get("valueQuantity", {}).get("value")
                unit = entry.get("valueQuantity", {}).get("unit")

                if value is not None and unit is not None:
                    try:
                        result = float(round(value, 1))
                        return f"{result} {unit}"
                    except (TypeError, ValueError):
                        return "LDL data is not a valid number"
                
                return "Complete LDL data not found"
            
            except (KeyError, IndexError):
                return "LDL data format is incorrect"

        # Single 
        try:
            value = obs_json.get("valueQuantity", {}).get("value")
            unit = obs_json.get("valueQuantity", {}).get("unit")
            
            if value is not None and unit is not None:
                try:
                    result = float(round(value, 1))
                    return f"{result} {unit}"
                except (TypeError, ValueError):
                    return "LDL data is not a valid number"
            
            return "No LDL data were found"
        
        except Exception:
            return "An unknown error occurred while processing LDL data"

    except Exception as e:
        system_logger.error(f"An error occurred while retrieving the LDL observation resource: {exception_message(e)}")
        raise ValueError(f"Found the following error pulling Observation FHIR resource: {exception_message(e)}") from e


async def get_tg(tokens):
    # Getting data in the way prescribed by OAuthLib package
    uri, headers, body = client.add_token(
        f"{credentialSettings.BASE_URL}/Observation?patient={tokens['patient']}&category=laboratory&code=2571-8",  # Triglycerides
        headers={"Accept": "application/fhir+json"},
    )

    try:
        obs_json = fetch_fhir_json(uri, headers, body)

        # Bundle
        if obs_json.get("resourceType") == "Bundle" and obs_json.get("total", 0) > 0:
            try:
                entry = obs_json["entry"][0]["resource"]
                value = entry.get("valueQuantity", {}).get("value")
                unit = entry.get("valueQuantity", {}).get("unit")

                if value is not None and unit is not None:
                    try:
                        result = float(round(value, 1))
                        return f"{result} {unit}"
                    except (TypeError, ValueError):
                        return "TG data is not a valid number"
                
                return "Complete TG data not found"
            
            except (KeyError, IndexError):
                return "TG data format is incorrect"

        # Single 
        try:
            value = obs_json.get("valueQuantity", {}).get("value")
            unit = obs_json.get("valueQuantity", {}).get("unit")
            
            if value is not None and unit is not None:
                try:
                    result = float(round(value, 1))
                    return f"{result} {unit}"
                except (TypeError, ValueError):
                    return "TG data is not a valid number"
            
            return "No TG data were found"
        
        except Exception:
            return "An unknown error occurred while processing TG data"

    except Exception as e:
        system_logger.error(f"An error occurred while retrieving the TG observation resource: {exception_message(e)}")
        raise ValueError(f"Found the following error pulling Observation FHIR resource: {exception_message(e)}") from e


async def get_chol(tokens):
    # Getting data in the way prescribed by OAuthLib package
    uri, headers, body = client.add_token(
        f"{credentialSettings.BASE_URL}/Observation?patient={tokens['patient']}&category=laboratory&code=2093-3",  # Total Cholesterol
        headers={"Accept": "application/fhir+json"},
    )

    try:
        obs_json = fetch_fhir_json(uri, headers, body)

        # Bundle
        if obs_json.get("resourceType") == "Bundle" and obs_json.get("total", 0) > 0:
            try:
                entry = obs_json["entry"][0]["resource"]
                value = entry.get("valueQuantity", {}).get("value")
                unit = entry.get("valueQuantity", {}).get("unit")

                if value is not None and unit is not None:
                    try:
                        result = float(round(value, 1))
                        return f"{result} {unit}"
                    except (TypeError, ValueError):
                        return "Cholesterol data is not a valid number"
                
                return "Complete Cholesterol data not found"
            
            except (KeyError, IndexError):
                return "Cholesterol data format is incorrect"

        # Single 
        try:
            value = obs_json.get("valueQuantity", {}).get("value")
            unit = obs_json.get("valueQuantity", {}).get("unit")
            
            if value is not None and unit is not None:
                try:
                    result = float(round(value, 1))
                    return f"{result} {unit}"
                except (TypeError, ValueError):
                    return "Cholesterol data is not a valid number"
            
            return "No Cholesterol data were found"
        
        except Exception:
            return "An unknown error occurred while processing Cholesterol data"

    except Exception as e:
        system_logger.error(f"An error occurred while retrieving the Cholesterol observation resource: {exception_message(e)}")
        raise ValueError(f"Found the following error pulling Observation FHIR resource: {exception_message(e)}") from e


async def get_scr(tokens):
    # Getting data in the way prescribed by OAuthLib package
    uri, headers, body = client.add_token(
        f"{credentialSettings.BASE_URL}/Observation?patient={tokens['patient']}&category=laboratory&code=38483-4",
        headers={"Accept": "application/fhir+json"},
    )

    try:
        obs_json = fetch_fhir_json(uri, headers, body)

        # Bundle
        if obs_json.get("resourceType") == "Bundle" and obs_json.get("total", 0) > 0:
            try:
                entry = obs_json["entry"][0]["resource"]
                value = entry.get("valueQuantity", {}).get("value")
                unit = entry.get("valueQuantity", {}).get("unit")

                if value is not None and unit is not None:
                    try:
                        result = float(round(value, 1))
                        return f"{result} {unit}"
                    except (TypeError, ValueError):
                        return "Serum Creatinine data is not a valid number"
                
                return "Complete Serum Creatinine data not found"
            
            except (KeyError, IndexError):
                return "Serum Creatinine data format is incorrect"

        # Single 
        try:
            value = obs_json.get("valueQuantity", {}).get("value")
            unit = obs_json.get("valueQuantity", {}).get("unit")
            
            if value is not None and unit is not None:
                try:
                    result = float(round(value, 1))
                    return f"{result} {unit}"
                except (TypeError, ValueError):
                    return "Serum Creatinine data is not a valid number"
            
            return "No Serum Creatinine data were found"
        
        except Exception:
            return "An unknown error occurred while processing Serum Creatinine data"

    except Exception as e:
        system_logger.error(f"An error occurred while retrieving the Serum Creatinine observation resource: {exception_message(e)}")
        raise ValueError(f"Found the following error pulling Observation FHIR resource: {exception_message(e)}") from e


def get_glucose(tokens):

    # Getting data in the way prescribed by OAuthLib package
    uri, headers, body = client.add_token(
        f"{credentialSettings.BASE_URL}/Observation?patient={tokens['patient']}&category=laboratory&code=2339-0",
        headers={"Accept": "application/fhir+json"},
    )

    try:
        obs_json = fetch_fhir_json(uri, headers, body)

        # Bundle
        if obs_json.get("resourceType") == "Bundle" and obs_json.get("total", 0) > 0:
            try:
                entry = obs_json["entry"][0]["resource"]
                value = entry.get("valueQuantity", {}).get("value")
                unit = entry.get("valueQuantity", {}).get("unit")

                if value is not None and unit is not None:
                    try:
                        result = float(round(value, 1))
                        return f"{result} {unit}"
                    except (TypeError, ValueError):
                        return "Glucose data is not a valid number"
                
                return "Complete Glucose data not found"
            
            except (KeyError, IndexError):
                return "Glucose data format is incorrect"

        # Single 
        try:
            value = obs_json.get("valueQuantity", {}).get("value")
            unit = obs_json.get("valueQuantity", {}).get("unit")
            
            if value is not None and unit is not None:
                try:
                    result = float(round(value, 1))
                    return f"{result} {unit}"
                except (TypeError, ValueError):
                    return "Glucose data is not a valid number"
            
            return "No Glucose data were found"
        
        except Exception:
            return "An unknown error occurred while processing Glucose data"

    except Exception as e:
        system_logger.error(f"An error occurred while retrieving the Glucose observation resource: {exception_message(e)}")
        raise ValueError(f"Found the following error pulling Observation FHIR resource: {exception_message(e)}") from e


def get_smoking_status(tokens):
    # Getting data in the way prescribed by OAuthLib package
    uri, headers, body = client.add_token(
        f"{credentialSettings.BASE_URL}/Observation?patient={tokens['patient']}&category=survey&code=72166-2",
        headers={"Accept": "application/fhir+json"},
    )
    try:
        obs_json = fetch_fhir_json(uri, headers, body)

        # Bundle
        if obs_json.get("resourceType") == "Bundle" and obs_json.get("total", 0) > 0:
            try:
                entry = obs_json["entry"][0]["resource"]
                value = entry.get("valueQuantity", {}).get("value")
                unit = entry.get("valueQuantity", {}).get("unit")

                if value is not None and unit is not None:
                    try:
                        result = float(round(value, 1))
                        return f"{result} {unit}"
                    except (TypeError, ValueError):
                        return "Smoking Status data is not a valid number"
                
                return "Complete Smoking Status data not found"
            
            except (KeyError, IndexError):
                return "Smoking Status data format is incorrect"

        # Single 
        try:
            value = obs_json.get("valueQuantity", {}).get("value")
            unit = obs_json.get("valueQuantity", {}).get("unit")
            
            if value is not None and unit is not None:
                try:
                    result = float(round(value, 1))
                    return f"{result} {unit}"
                except (TypeError, ValueError):
                    return "Smoking Status data is not a valid number"
            
            return "No Smoking Status data were found"
        
        except Exception:
            return "An unknown error occurred while processing Smoking Status data"

    except Exception as e:
        system_logger.error(f"An error occurred while retrieving the Smoking Status observation resource: {exception_message(e)}")
        raise ValueError(f"Found the following error pulling Observation FHIR resource: {exception_message(e)}") from e


#### 路由
## [GET] : height
@router.get("/heights", name="Get Heights", description="Get heights (value + unit)")
async def get_height_route(height=Depends(get_height)):
    return height

## [GET] : weight
@router.get("/weights", name="Get Weights", description="Get weights (value + unit)")
async def get_weight_route(weight=Depends(get_weight)):
    return weight

## [GET] : BMI
@router.get("/bmi", name="Get Body Mass Index", description="Get body mass index (BMI) (value + unit)")
async def get_bmi_route(bmi=Depends(get_bmi)):
    return bmi

## [GET] : BP
@router.get("/bp", name="Get Blood Pressure", description="Get blood pressure (value + unit)")
async def get_bp(sbp, dbp=Depends(get_bp)):
    return sbp, dbp

## [GET] : HDL
@router.get("/hdl", name="Get High-density Lipoprotein", description="Get high-density lipoprotein (value + unit)")
async def get_hdl_route(hdl=Depends(get_hdl)):
    return hdl
    
## [GET] : LDL
@router.get("/ldl", name="Get Low-density Lipoprotein", description="Get low-density lipoprotein (value + unit)")
async def get_ldl_route(ldl=Depends(get_ldl)):
    return ldl

## [GET] : TG
@router.get("/tg", name="Get Triglycerides", description="Get triglycerides (value + unit)")
async def get_tg_route(tg=Depends(get_tg)):
    return tg

## [GET] : Cholesterol
@router.get("/cholesterol", name="Get Cholesterol", description="Get cholesterol (value + unit)")
async def get_chol_route(chol=Depends(get_chol)):
    return chol

## [GET] : SCr
@router.get("/scr", name="Get Serum Creatinine (Cr/SCr)", description="Get serum creatinine (Cr/SCr) (value + unit)")
async def get_scr_route(scr=Depends(get_scr)):
    return scr

## [GET] : Glucose
@router.get("/glucose", name="Get Glucose (Blood Sugar)", description="Get glucose (blood sugar, BS) (value + unit)")
def get_glucose_route(glucose=Depends(get_glucose)):
    return glucose

## [GET] : Smoking Status
@router.get("/smoking-status", name="Get Smoking Status", description="Get smoking status")
def get_smoking_status_route(smoking_status=Depends(get_smoking_status)):
    return smoking_status
