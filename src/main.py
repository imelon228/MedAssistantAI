from fastapi import FastAPI
from src.models import DiagnoseRequest, DiagnoseResponse, Diagnosis
from src.vector_db import search_protocols

app = FastAPI(
    title="Medical Diagnosis AI",
    description="Symptoms → ICD-10 diagnostic system",
)

@app.get("/")
def root():
    return {"status": "running"}

@app.post("/diagnose", response_model=DiagnoseResponse)
def diagnose(request: DiagnoseRequest):

    symptoms = request.symptoms

    protocols = search_protocols(symptoms)

    diagnoses = []

    for rank, protocol in enumerate(protocols, start=1):

        diagnoses.append(
            Diagnosis(
                rank=rank,
                diagnosis=protocol["title"],
                icd10_code=protocol["icd_code"],
                explanation=protocol["text"][:300]
            )
        )

    return DiagnoseResponse(diagnoses=diagnoses)