import logging
# import datetime
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from oauthlib.oauth2 import WebApplicationClient
from icecream import ic
import httpx

from app.configs.config import credentialSettings
from app.models.patient import PatientDataResponse
from app.middleware.exception import exception_message
from app.middleware.function import fetch_fhir_json


router = APIRouter()

client = WebApplicationClient(credentialSettings.CLIENT_ID)

uvicorn_logger = logging.getLogger('uvicorn.error')
system_logger = logging.getLogger('custom.error')

#### 依賴函數
async def get_patient_data(uri, headers, patient_token):

    try:
        ic("222222")
        # Getting data in the way prescribed by OAuthLib package
        async with httpx.AsyncClient() as asynclient:
            # response = await asynclient.get(uri, headers=headers, data=body, timeout=10)
            response = await asynclient.get(uri, headers=headers, timeout=10)
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Failed to load patient data.")
            ic(response.status_code)

            fhir_json = response.json()
        ic(fhir_json)

        # Sometimes a resource is returned, but it doesn't have anything useful
        if fhir_json["resourceType"] == "OperationOutcome":
            raise ValueError(
                f"""
                The patient you selected (FHIR ID: {patient_token})
                does not have patient data available
                """
            )
        ic(fhir_json)

        # Get the patient name
        try:
            name = fhir_json["name"][0]["text"].title()
            given_name = name.split(" ")[0].lower().title()
            family_name = name.split(" ")[1].lower().title()
        except KeyError:
            try:
                given_name = fhir_json["name"][0]["given"][0].lower().title()
                family_name = fhir_json["name"][0]["family"].lower().title()
            except KeyError:
                print(
                    f"""
                    Patient FHIR ID {patient_token} has either a
                    missing given name or a missing family name
                    """
                )

        # Get Date of Birth
        try:
            birth_date = fhir_json["birthDate"]
        except KeyError:
            birth_date = "No birth date specified in FHIR data"
        
        # Calculate Age
        try:
            if birth_date is not None:
                birth_year = int(birth_date.split('-')[0])
                current_year = datetime.now().year
                age = current_year - birth_year
        except KeyError:
            age = "No birth date specified in FHIR data"
        
         # Get Gender
        try:
            gender = fhir_json["gender"]
        except KeyError:
            gender = "No gender specified in FHIR data"

        # Get Race
        try:
            race = fhir_json["extension"][0]["extension"][1]["valueString"]
        except KeyError:
            race = "No race specified in FHIR data"

        # Get Ethnicity
        try:
            ethnicity = fhir_json["extension"][1]["extension"][1]["valueString"]
        except KeyError:
            ethnicity = "No ethnicity specified in FHIR data"

    except Exception as e:
        system_logger.error(f"An error occurred while retrieving the Patient resource: {exception_message(e)}")
        raise ValueError(f"Found the following error pulling Paitent FHIR resource: {exception_message(e)}") from e

    return given_name, family_name, birth_date, age, gender, race, ethnicity


#### 路由
## [GET] : given_name, family_name, birth_date, age, gender, race, ethnicity
# @router.get("", name="Get Basic Patient Data", description="Get basic patient data, including given_name, family_name, birth_date, age, gender, race, ethnicity")
# async def get_patient_data_route(given_name, family_name, birth_date, age, gender, race, ethnicity=Depends(get_patient_data)):
#     return given_name, family_name, birth_date, age, gender, race, ethnicity

# @router.get("", response_model=PatientDataResponse)
# async def get_patient_data_route(tokens: dict):
#     given_name, family_name, birth_date, age, gender, race, ethnicity = await get_patient_data(tokens)
#     return PatientDataResponse(
#         given_name=given_name,
#         family_name=family_name,
#         birth_date=birth_date,
#         age=age,
#         gender=gender,
#         race=race,
#         ethnicity=ethnicity
#     )