from fastapi import FastAPI
from pydantic import BaseModel
from src.vector_db import search_protocols

app = FastAPI()

class DiagnoseRequest(BaseModel):
    symptoms: str

@app.post("/diagnose")
def diagnose(req: DiagnoseRequest):

    protocols = search_protocols(req.symptoms)

    diagnoses = []

    for i, protocol in enumerate(protocols):

        diagnoses.append({
            "rank": i+1,
            "diagnosis": protocol["title"],
            "icd10_code": protocol["icd_code"],
            "explanation": protocol["text"][:200]
        })

    return {"diagnoses": diagnoses}