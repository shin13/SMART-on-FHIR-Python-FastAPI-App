import logging
from datetime import datetime
from fastapi import APIRouter
from app.middleware.exception import exception_message
from icecream import ic


router = APIRouter()

uvicorn_logger = logging.getLogger('uvicorn.error')
system_logger = logging.getLogger('custom.error')


#### 依賴函數
async def extract_patient_info(fhir_json):
    try:
        if fhir_json["resourceType"] == "OperationOutcome":
            raise ValueError(
                f"""
                The patient you selected
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
                    Patient has either a missing given name or a missing family name
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

