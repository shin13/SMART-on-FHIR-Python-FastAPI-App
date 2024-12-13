import logging
from icecream import ic
from fastapi import APIRouter
from app.middleware.exception import exception_message
from app.middleware.function import extract_observation_data


router = APIRouter()

uvicorn_logger = logging.getLogger('uvicorn.error')
system_logger = logging.getLogger('custom.error')


#### 依賴函數
async def extract_height(fhir_json):
    return await extract_observation_data(fhir_json, "height")

async def extract_weight(fhir_json):
    return await extract_observation_data(fhir_json, "weight")

async def extract_bmi(fhir_json):
    return await extract_observation_data(fhir_json, "BMI")

async def extract_bp(fhir_json):
    try:
        # Bundle
        if fhir_json.get("resourceType") == "Bundle" and fhir_json.get("total", 0) > 0:
            try:
                entry = fhir_json["entry"][0]["resource"]
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
        if fhir_json.get("resourceType") == "Observation":
            try:
                components = fhir_json.get("component", [])
                
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


async def extract_hdl(fhir_json):
    return await extract_observation_data(fhir_json, "HDL")

async def extract_ldl(fhir_json):
    return await extract_observation_data(fhir_json, "LDL")

async def extract_tg(fhir_json):
    return await extract_observation_data(fhir_json, "triglyceride")

async def extract_chol(fhir_json):
    return await extract_observation_data(fhir_json, "cholesterol")

async def extract_scr(fhir_json):
    return await extract_observation_data(fhir_json, "serum creatinine")

async def extract_glucose(fhir_json):
    return await extract_observation_data(fhir_json, "blood glucose")

async def extract_smoking_status(fhir_json):
    return await extract_observation_data(fhir_json, "smoking satus")


# #### 路由
# ## [GET] : height
# @router.get("/heights", name="Get Heights", description="Get heights (value + unit)")
# async def get_height_route(height=Depends(get_height)):
#     return height

# ## [GET] : weight
# @router.get("/weights", name="Get Weights", description="Get weights (value + unit)")
# async def get_weight_route(weight=Depends(get_weight)):
#     return weight

# ## [GET] : BMI
# @router.get("/bmi", name="Get Body Mass Index", description="Get body mass index (BMI) (value + unit)")
# async def get_bmi_route(bmi=Depends(get_bmi)):
#     return bmi

# ## [GET] : BP
# @router.get("/bp", name="Get Blood Pressure", description="Get blood pressure (value + unit)")
# async def get_bp(sbp, dbp=Depends(get_bp)):
#     return sbp, dbp

# ## [GET] : HDL
# @router.get("/hdl", name="Get High-density Lipoprotein", description="Get high-density lipoprotein (value + unit)")
# async def get_hdl_route(hdl=Depends(get_hdl)):
#     return hdl
    
# ## [GET] : LDL
# @router.get("/ldl", name="Get Low-density Lipoprotein", description="Get low-density lipoprotein (value + unit)")
# async def get_ldl_route(ldl=Depends(get_ldl)):
#     return ldl

# ## [GET] : TG
# @router.get("/tg", name="Get Triglycerides", description="Get triglycerides (value + unit)")
# async def get_tg_route(tg=Depends(get_tg)):
#     return tg

# ## [GET] : Cholesterol
# @router.get("/cholesterol", name="Get Cholesterol", description="Get cholesterol (value + unit)")
# async def get_chol_route(chol=Depends(get_chol)):
#     return chol

# ## [GET] : SCr
# @router.get("/scr", name="Get Serum Creatinine (Cr/SCr)", description="Get serum creatinine (Cr/SCr) (value + unit)")
# async def get_scr_route(scr=Depends(get_scr)):
#     return scr

# ## [GET] : Glucose
# @router.get("/glucose", name="Get Glucose (Blood Sugar)", description="Get glucose (blood sugar, BS) (value + unit)")
# def get_glucose_route(glucose=Depends(get_glucose)):
#     return glucose

# ## [GET] : Smoking Status
# @router.get("/smoking-status", name="Get Smoking Status", description="Get smoking status")
# def get_smoking_status_route(smoking_status=Depends(get_smoking_status)):
#     return smoking_status
