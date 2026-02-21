from pydantic import BaseModel
from typing import List

class DiagnoseRequest(BaseModel):
    symptoms: str

class Diagnosis(BaseModel):
    rank: int
    diagnosis: str
    icd10_code: str
    explanation: str

class DiagnoseResponse(BaseModel):
    diagnoses: List[Diagnosis]