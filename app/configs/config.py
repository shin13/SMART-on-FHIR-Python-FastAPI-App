from pydantic.v1 import BaseSettings

class Settings():
    VERSION: str = "beta0.1"
    API_PREFIX: str = "/api/v1"


basicSettings = Settings()


class Settings():
    CLIENT_ID = "client-id"
    BASE_URL = "https://launch.smarthealthit.org/v/r4/fhir"

    # For EHR launch, the scope should be "launch", not "launch/patient"
    SCOPES = (
        "patient/Patient.rs patient/Observation.rs launch offline_access openid fhirUser"
    )

    REDIRECT_URI = "http://localhost:4201/fhir-app/"
    # REDIRECT_URI = "https://smart-on-fhir-python-app.onrender.com/fhir-app/"


credentialSettings = Settings()