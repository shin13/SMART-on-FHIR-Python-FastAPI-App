import json
import requests
from fastapi import APIRouter, Depends, HTTPException, Query
from oauthlib.oauth2 import WebApplicationClient

from app.configs.config import credentialSettings
from app.middleware.exception import exception_message


router = APIRouter()
client = WebApplicationClient(credentialSettings.CLIENT_ID)


@router.get("/heights", name="Get observation/heights", description="Get observation/heights (value + unit)")
async def get_height(tokens):

    # Getting data in the way prescribed by OAuthLib package
    uri, headers, body = client.add_token(
        f"{credentialSettings.BASE_URL}/Observation?patient={tokens['patient']}&category=vital-signs&code=8302-2",
        headers={"Accept": "application/fhir+json"},
    )

    try:
        # Getting data in the way prescribed by OAuthLib package
        observation = requests.get(uri, headers=headers, data=body, timeout=10)

        try:
            observation = observation.json()
        except json.JSONDecodeError as error:
            raise ValueError(
                """
                Observation data not returned in JSON format.  
                You probably haven't set the correct scope permissions,  
                or registered the app with the EHR vendor  
                so that it has access to this resource in Read or Search mode.
                """
            ) from error

        # Sometimes a resource is returned, but it doesn't have anything useful
        if observation["resourceType"] == "OperationOutcome":
            height = "No height data available due to OperationOutcome error"
        else:
            if observation["resourceType"] == "Bundle" and observation["total"] > 0:
                entry = observation["entry"][0]
                try:
                    value = entry["resource"]["valueQuantity"]["value"]
                    unit = entry["resource"]["valueQuantity"]["unit"]
                    height = str(round(value, 1)) + " " + unit
                except KeyError:
                    height = "No valid height data available. Either there isn't a value or a unit."

            else:
                height = "No height data available due to empty bundle"

    except Exception as error:
        raise ValueError(
            f"Found the following error pulling Observation FHIR resource: {error}"
        ) from error

    return height


@router.get("/weights", name="Get observation/weights", description="Get observation/weights (value + unit)")
async def get_weight(tokens):

    # Getting data in the way prescribed by OAuthLib package
    uri, headers, body = client.add_token(
        f"{credentialSettings.BASE_URL}/Observation?patient={tokens['patient']}&category=vital-signs&code=29463-7",
        headers={"Accept": "application/fhir+json"},
    )

    try:
        # Getting data in the way prescribed by OAuthLib package
        observation = requests.get(uri, headers=headers, data=body, timeout=10)

        try:
            observation = observation.json()
        except json.JSONDecodeError as error:
            raise ValueError(
                """
                Observation data not returned in JSON format.  
                You probably haven't set the correct scope permissions,  
                or registered the app with the EHR vendor  
                so that it has access to this resource in Read or Search mode.
                """
            ) from error

        # Sometimes a resource is returned, but it doesn't have anything useful
        if observation["resourceType"] == "OperationOutcome":
            weight = "No weight data available due to OperationOutcome error"
        else:
            if observation["resourceType"] == "Bundle" and observation["total"] > 0:
                entry = observation["entry"][0]
                try:
                    value = entry["resource"]["valueQuantity"]["value"]
                    unit = entry["resource"]["valueQuantity"]["unit"]
                    weight = str(round(value, 1)) + " " + unit
                except KeyError:
                    weight = "No valid weight data available. Either there isn't a value or a unit."

            else:
                weight = "No weight data available due to empty bundle"

    except Exception as error:
        raise ValueError(
            f"Found the following error pulling Observation FHIR resource: {error}"
        ) from error

    return weight


@router.get("/bmi", name="Get observation/body mass index (BMI)", description="Get observation/body mass index (BMI) (value + unit)")
async def get_bmi(tokens):

    # Getting data in the way prescribed by OAuthLib package
    uri, headers, body = client.add_token(
        f"{credentialSettings.BASE_URL}/Observation?patient={tokens['patient']}&category=vital-signs&code=39156-5",
        headers={"Accept": "application/fhir+json"},
    )

    try:
        # Getting data in the way prescribed by OAuthLib package
        observation = requests.get(uri, headers=headers, data=body, timeout=10)

        try:
            observation = observation.json()
        except json.JSONDecodeError as error:
            raise ValueError(
                """
                Observation data not returned in JSON format.  
                You probably haven't set the correct scope permissions,  
                or registered the app with the EHR vendor  
                so that it has access to this resource in Read or Search mode.
                """
            ) from error

        # Sometimes a resource is returned, but it doesn't have anything useful
        if observation["resourceType"] == "OperationOutcome":
            bmi = "No Body Mass Index (BMI) data available due to OperationOutcome error"
        else:
            if observation["resourceType"] == "Bundle" and observation["total"] > 0:
                entry = observation["entry"][0]
                try:
                    value = entry["resource"]["valueQuantity"]["value"]
                    unit = entry["resource"]["valueQuantity"]["unit"]
                    bmi = str(round(value, 1)) + " " + unit
                except KeyError:
                    bmi = "No valid Body Mass Index (BMI) data available. Either there isn't a value or a unit."

            else:
                bmi = "No Body Mass Index (BMI) data available due to empty bundle"

    except Exception as error:
        raise ValueError(
            f"Found the following error pulling Observation FHIR resource: {error}"
        ) from error

    return bmi


@router.get("/bp", name="Get observation/blood pressure (BP)", description="Get observation/blood pressure (BP) (value + unit)")
async def get_bp(tokens):
    # Getting data in the way prescribed by OAuthLib package
    uri, headers, body = client.add_token(
        f"{credentialSettings.BASE_URL}/Observation?patient={tokens['patient']}&category=vital-signs&code=55284-4",
        headers={"Accept": "application/fhir+json"},
    )

    try:
        # Getting data in the way prescribed by OAuthLib package
        blood_pressure = requests.get(uri, headers=headers, data=body, timeout=10)

        try:
            blood_pressure = blood_pressure.json()
        except json.JSONDecodeError as error:
            raise ValueError(
                """
                Observation data not returned in JSON format.  
                You probably haven't set the correct scope permissions,  
                or registered the app with the EHR vendor  
                so that it has access to this resource in Read or Search mode.
                """
            ) from error

        # Sometimes a resource is returned, but it doesn't have anything useful
        if blood_pressure["resourceType"] == "OperationOutcome":
            sys_bp = (
                "No systolic blood pressure available due to OperationOutcome error"
            )
            dias_bp = (
                "No diastolic blood pressure available due to OperationOutcome error"
            )
        else:
            if (
                blood_pressure["resourceType"] == "Bundle"
                and blood_pressure["total"] > 0
            ):
                entry = blood_pressure["entry"][0]
                try:
                    sys_value = entry["resource"]["component"][0]["valueQuantity"][
                        "value"
                    ]
                    sys_unit = entry["resource"]["component"][0]["valueQuantity"][
                        "unit"
                    ]
                    sys_bp = str(round(sys_value, 1)) + " " + sys_unit
                except KeyError:
                    sys_bp = "No valid systolic blood pressure available. Either there wasn't a value or a unit."

                try:
                    dias_value = entry["resource"]["component"][1]["valueQuantity"][
                        "value"
                    ]
                    dias_unit = entry["resource"]["component"][1]["valueQuantity"][
                        "unit"
                    ]
                    dias_bp = str(round(dias_value, 1)) + " " + dias_unit
                except KeyError:
                    dias_bp = "No valid diastolic blood pressure available. Either there wasn't a value or a unit."

            else:
                sys_bp = "No systolic blood pressure available due to empty bundle"
                dias_bp = "No diastolic blood pressure available due to empty bundle"

    except Exception as error:
        raise ValueError(
            f"Found the following error pulling Observation FHIR resource: {error}"
        ) from error

    return sys_bp, dias_bp


@router.get("/hdl", name="Get observation/hdl", description="Get observation/hdl (value + unit)")
async def get_hdl(tokens):

    # Getting data in the way prescribed by OAuthLib package
    uri, headers, body = client.add_token(
        f"{credentialSettings.BASE_URL}/Observation?patient={tokens['patient']}&category=laboratory&code=2085-9",
        headers={"Accept": "application/fhir+json"},
    )

    try:
        # Getting data in the way prescribed by OAuthLib package
        hdl = requests.get(uri, headers=headers, data=body, timeout=10)

        try:
            hdl = hdl.json()
        except json.JSONDecodeError as error:
            raise ValueError(
                """
                Observation data not returned in JSON format.  
                You probably haven't set the correct scope permissions,  
                or registered the app with the EHR vendor  
                so that it has access to this resource in Read or Search mode.
                """
            ) from error

        # Sometimes a resource is returned, but it doesn't have anything useful
        if hdl["resourceType"] == "OperationOutcome":
            good_chol = "No HDL available due to OperationOutcome error"
        else:
            if hdl["resourceType"] == "Bundle" and hdl["total"] > 0:
                entry = hdl["entry"][0]
                try:
                    value = entry["resource"]["valueQuantity"]["value"]
                    unit = entry["resource"]["valueQuantity"]["unit"]
                    good_chol = str(round(value, 1)) + " " + unit
                except KeyError:
                    good_chol = (
                        "No HDL available. Either there wasn't a value or a unit."
                    )

            else:
                good_chol = "No HDL available due to empty bundle"

    except Exception as error:
        raise ValueError(
            f"Found the following error pulling Observation FHIR resource: {error}"
        ) from error

    return good_chol


@router.get("/ldl", name="Get observation/ldl", description="Get observation/ldl (value + unit)")
async def get_ldl(tokens):
    # Getting data in the way prescribed by OAuthLib package
    uri, headers, body = client.add_token(
        f"{credentialSettings.BASE_URL}/Observation?patient={tokens['patient']}&category=laboratory&code=18262-6",
        headers={"Accept": "application/fhir+json"},
    )

    try:
        # Getting data in the way prescribed by OAuthLib package
        ldl = requests.get(uri, headers=headers, data=body, timeout=10)

        try:
            ldl = ldl.json()
        except json.JSONDecodeError as error:
            raise ValueError(
                """
                Observation data not returned in JSON format.  
                You probably haven't set the correct scope permissions,  
                or registered the app with the EHR vendor  
                so that it has access to this resource in Read or Search mode.
                """
            ) from error

        # Sometimes a resource is returned, but it doesn't have anything useful
        if ldl["resourceType"] == "OperationOutcome":
            bad_chol = "No LDL available due to OperationOutcome error"
        else:
            if ldl["resourceType"] == "Bundle" and ldl["total"] > 0:
                entry = ldl["entry"][0]
                try:
                    value = entry["resource"]["valueQuantity"]["value"]
                    unit = entry["resource"]["valueQuantity"]["unit"]
                    bad_chol = str(round(value, 1)) + " " + unit
                except KeyError:
                    bad_chol = (
                        "No LDL available. Either there wasn't a value or a unit."
                    )

            else:
                bad_chol = "No LDL available due to empty bundle"

    except Exception as error:
        raise ValueError(
            f"Found the following error pulling Observation FHIR resource: {error}"
        ) from error

    return bad_chol


@router.get("/tg", name="Get observation/triglycerides (TG)", description="Get observation/triglycerides (TG) (value + unit)")
async def get_tg(tokens):
    # Getting data in the way prescribed by OAuthLib package
    uri, headers, body = client.add_token(
        f"{credentialSettings.BASE_URL}/Observation?patient={tokens['patient']}&category=laboratory&code=2571-8",  # Triglycerides
        headers={"Accept": "application/fhir+json"},
    )

    try:
        # Getting data in the way prescribed by OAuthLib package
        tg = requests.get(uri, headers=headers, data=body, timeout=10)

        try:
            tg = tg.json()
        except json.JSONDecodeError as error:
            raise ValueError(
                """
                Observation data not returned in JSON format.  
                You probably haven't set the correct scope permissions,  
                or registered the app with the EHR vendor  
                so that it has access to this resource in Read or Search mode.
                """
            ) from error

        # Sometimes a resource is returned, but it doesn't have anything useful
        if tg["resourceType"] == "OperationOutcome":
            triglyceride = "No triglycerides available due to OperationOutcome error"
        else:
            if tg["resourceType"] == "Bundle" and tg["total"] > 0:
                entry = tg["entry"][0]
                try:
                    value = entry["resource"]["valueQuantity"]["value"]
                    unit = entry["resource"]["valueQuantity"]["unit"]
                    triglycerides = str(round(value, 1)) + " " + unit
                except KeyError:
                    triglycerides = (
                        "No triglycerides available. Either there wasn't a value or a unit."
                    )

            else:
                triglycerides = "No triglycerides available due to empty bundle"

    except Exception as error:
        raise ValueError(
            f"Found the following error pulling Observation FHIR resource: {error}"
        ) from error

    return triglycerides


@router.get("/cholesterol", name="Get observation/cholesterol", description="Get observation/cholesterol (value + unit)")
async def get_chol(tokens):
    # Getting data in the way prescribed by OAuthLib package
    uri, headers, body = client.add_token(
        f"{credentialSettings.BASE_URL}/Observation?patient={tokens['patient']}&category=laboratory&code=2093-3",  # Total Cholesterol
        headers={"Accept": "application/fhir+json"},
    )

    try:
        # Getting data in the way prescribed by OAuthLib package
        chol = requests.get(uri, headers=headers, data=body, timeout=10)

        try:
            chol = chol.json()
        except json.JSONDecodeError as error:
            raise ValueError(
                """
                Observation data not returned in JSON format.  
                You probably haven't set the correct scope permissions,  
                or registered the app with the EHR vendor  
                so that it has access to this resource in Read or Search mode.
                """
            ) from error

        # Sometimes a resource is returned, but it doesn't have anything useful
        if chol["resourceType"] == "OperationOutcome":
            cholesterol = "No cholesterol available due to OperationOutcome error"
        else:
            if chol["resourceType"] == "Bundle" and chol["total"] > 0:
                entry = chol["entry"][0]
                try:
                    value = entry["resource"]["valueQuantity"]["value"]
                    unit = entry["resource"]["valueQuantity"]["unit"]
                    cholesterol = str(round(value, 1)) + " " + unit
                except KeyError:
                    cholesterol = (
                        "No cholesterol available. Either there wasn't a value or a unit."
                    )

            else:
                cholesterol = "No cholesterol available due to empty bundle"

    except Exception as error:
        raise ValueError(
            f"Found the following error pulling Observation FHIR resource: {error}"
        ) from error

    return cholesterol


@router.get("/scr", name="Get observation/serum creatinine (Cr/SCr)", description="Get observation/serum creatinine (Cr/SCr) (value + unit)")
async def get_scr(tokens):
    # Getting data in the way prescribed by OAuthLib package
    uri, headers, body = client.add_token(
        f"{credentialSettings.BASE_URL}/Observation?patient={tokens['patient']}&category=laboratory&code=38483-4",
        headers={"Accept": "application/fhir+json"},
    )

    try:
        # Getting data in the way prescribed by OAuthLib package
        cr = requests.get(uri, headers=headers, data=body, timeout=10)

        try:
            cr = cr.json()
        except json.JSONDecodeError as error:
            raise ValueError(
                """
                Observation data not returned in JSON format.  
                You probably haven't set the correct scope permissions,  
                or registered the app with the EHR vendor  
                so that it has access to this resource in Read or Search mode.
                """
            ) from error

        # Sometimes a resource is returned, but it doesn't have anything useful
        if cr["resourceType"] == "OperationOutcome":
            cr = "No creatinine available due to OperationOutcome error"
        else:
            if cr["resourceType"] == "Bundle" and cr["total"] > 0:
                entry = cr["entry"][0]
                try:
                    value = entry["resource"]["valueQuantity"]["value"]
                    unit = entry["resource"]["valueQuantity"]["unit"]
                    cr = str(round(value, 1)) + " " + unit
                except KeyError:
                    cr = (
                        "No creatinine available. Either there wasn't a value or a unit."
                    )

            else:
                cr = "No creatinine available due to empty bundle"

    except Exception as error:
        raise ValueError(
            f"Found the following error pulling Observation FHIR resource: {error}"
        ) from error

    return cr


@router.get("/glucose", name="Get observation/glucose (blood sugar, BS)", description="Get observation/glucose (blood sugar, BS) (value + unit)")
def get_glucose(tokens):

    # Getting data in the way prescribed by OAuthLib package
    uri, headers, body = client.add_token(
        f"{credentialSettings.BASE_URL}/Observation?patient={tokens['patient']}&category=laboratory&code=2339-0",
        headers={"Accept": "application/fhir+json"},
    )

    try:
        # Getting data in the way prescribed by OAuthLib package
        glucose = requests.get(uri, headers=headers, data=body, timeout=10)

        try:
            glucose = glucose.json()
        except json.JSONDecodeError as error:
            raise ValueError(
                """
                Observation data not returned in JSON format.  
                You probably haven't set the correct scope permissions,  
                or registered the app with the EHR vendor  
                so that it has access to this resource in Read or Search mode.
                """
            ) from error

        # Sometimes a resource is returned, but it doesn't have anything useful
        if glucose["resourceType"] == "OperationOutcome":
            glucose = "No glucose available due to OperationOutcome error"
        else:
            if glucose["resourceType"] == "Bundle" and glucose["total"] > 0:
                entry = glucose["entry"][0]
                try:
                    value = entry["resource"]["valueQuantity"]["value"]
                    unit = entry["resource"]["valueQuantity"]["unit"]
                    glucose = str(round(value, 1)) + " " + unit
                except KeyError:
                    glucose = (
                        "No glucose available. Either there wasn't a value or a unit."
                    )

            else:
                glucose = "No glucose available due to empty bundle"

    except Exception as error:
        raise ValueError(
            f"Found the following error pulling Observation FHIR resource: {error}"
        ) from error

    return glucose


@router.get("/smoking-status", name="Get observation/smoking status", description="Get observation/smoking status")
def get_smoking_status(tokens):
    # Getting data in the way prescribed by OAuthLib package
    uri, headers, body = client.add_token(
        f"{credentialSettings.BASE_URL}/Observation?patient={tokens['patient']}&category=survey&code=72166-2",
        headers={"Accept": "application/fhir+json"},
    )

    try:
        # Getting data in the way prescribed by OAuthLib package
        observation = requests.get(uri, headers=headers, data=body, timeout=10)

        try:
            observation = observation.json()
        except json.JSONDecodeError as error:
            raise ValueError(
                """
                Observation data not returned in JSON format.  
                You probably haven't set the correct scope permissions,  
                or registered the app with the EHR vendor  
                so that it has access to this resource in Read or Search mode.
                """
            ) from error

        # Sometimes a resource is returned, but it doesn't have anything useful
        if observation["resourceType"] == "OperationOutcome":
            smoke = "No smoking status data available due to OperationOutcome error"
        else:
            if observation["resourceType"] == "Bundle" and observation["total"] > 0:
                entry = observation["entry"][0]
                try:
                    smoke = entry["resource"]["valueCodeableConcept"]["text"]
                except KeyError:
                    smoke = "No valid data available."

            else:
                smoke = "No smoking status data available due to empty bundle"

    except Exception as error:
        raise ValueError(
            f"Found the following error pulling Observation FHIR resource: {error}"
        ) from error

    return smoke


