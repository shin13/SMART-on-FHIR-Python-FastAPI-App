import requests
import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from oauthlib.oauth2 import WebApplicationClient

from app.configs.config import credentialSettings
from app.middleware.exception import exception_message


router = APIRouter()
client = WebApplicationClient(credentialSettings.CLIENT_ID)


@router.get("", name="Get basic patient data", description="Get basic patient data, including given_name, family_name, birth_date, age, gender, race, ethnicity")
async def get_patient_data(tokens):

    # Getting data in the way prescribed by OAuthLib package
    uri, headers, body = client.add_token(
        f"{credentialSettings.BASE_URL}/Patient/{tokens['patient']}",
        headers={"Accept": "application/fhir+json"},
    )

    try:
        # Getting data in the way prescribed by OAuthLib package
        patient = requests.get(uri, headers=headers, data=body, timeout=10).json()

        # Sometimes a resource is returned, but it doesn't have anything useful
        if patient["resourceType"] == "OperationOutcome":
            # print(f"\n{patient}\n")
            raise ValueError(
                f"""
                The patient you selected (FHIR ID: {tokens['patient']})
                does not have patient data available
                """
            )

        # Get the patient name
        try:
            name = patient["name"][0]["text"].title()
            given_name = name.split(" ")[0].lower().title()
            family_name = name.split(" ")[1].lower().title()
        except KeyError:
            try:
                given_name = patient["name"][0]["given"][0].lower().title()
                family_name = patient["name"][0]["family"].lower().title()
            except KeyError:
                print(
                    f"""
                    Patient FHIR ID {tokens['patient']} has either a
                    missing given name or a missing family name
                    """
                )

        # Get Date of Birth
        try:
            birth_date = patient["birthDate"]
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
            gender = patient["gender"]
        except KeyError:
            gender = "No gender specified in FHIR data"

        # Get Race
        try:
            race = patient["extension"][0]["extension"][1]["valueString"]
        except KeyError:
            race = "No race specified in FHIR data"

        # Get Ethnicity
        try:
            ethnicity = patient["extension"][1]["extension"][1]["valueString"]
        except KeyError:
            ethnicity = "No ethnicity specified in FHIR data"



    except Exception as error:
        raise ValueError(
            f"Found the following error pulling Patient FHIR resource: {error}"
        ) from error

    return given_name, family_name, birth_date, age, gender, race, ethnicity