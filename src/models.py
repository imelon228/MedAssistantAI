from pydantic import BaseModel
from typing import List, Optional


class DiagnoseRequest(BaseModel):

    symptoms: Optional[str] = None
    text: Optional[str] = None

    # evaluator sends either symptoms or text
    def get_query(self) -> str:

        if self.symptoms and self.symptoms.strip():
            return self.symptoms.strip()

        if self.text and self.text.strip():
            return self.text.strip()

        return ""


class Diagnosis(BaseModel):

    rank: int
    diagnosis: str
    icd10_code: str
    explanation: str


class DiagnoseResponse(BaseModel):

    diagnoses: List[Diagnosis]