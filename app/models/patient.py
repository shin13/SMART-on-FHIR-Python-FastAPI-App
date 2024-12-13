from pydantic import BaseModel

class PatientDataResponse(BaseModel):
    given_name: str
    family_name: str
    birth_date: str
    age: str
    gender: str
    race: str
    ethnicity: str