from fastapi import FastAPI
from src.models import DiagnoseRequest, DiagnoseResponse, Diagnosis
from src.vector_db import search_protocols
from src.llm import ask_llm

import json


app = FastAPI(
    title="Medical Diagnosis AI",
    description="Symptoms → ICD-10 diagnostic system",
)


@app.get("/")
def root():
    return {"status": "running"}


@app.post("/diagnose", response_model=DiagnoseResponse)
def diagnose(request: DiagnoseRequest):

    try:

        # FIX 1 — правильное получение текста
        symptoms = request.get_query()

        if not symptoms or not symptoms.strip():
            return DiagnoseResponse(diagnoses=[])

        # vector search
        protocols = search_protocols(symptoms)

        if not protocols:
            return DiagnoseResponse(diagnoses=[])

        # build LLM context
        context = "\n\n".join(
            f"Diagnosis: {p['title']}\n"
            f"ICD10: {p['icd10_code']}\n"
            f"Text: {p['text'][:500]}"
            for p in protocols
        )

        # call LLM
        llm_result = ask_llm(symptoms, context)

        # FIX 2 — convert string → dict safely
        if isinstance(llm_result, str):

            try:
                llm_result = json.loads(llm_result)
            except:
                llm_result = {}

        diagnoses = []

        llm_diagnoses = llm_result.get("diagnoses", [])

        # FIX 3 — fallback if LLM failed
        if not llm_diagnoses:

            for i, p in enumerate(protocols[:3]):

                diagnoses.append(
                    Diagnosis(
                        rank=i + 1,
                        diagnosis=str(p["title"]),
                        icd10_code=str(p["icd10_code"]),
                        explanation=str(p["text"])[:300],
                    )
                )

        else:

            for item in llm_diagnoses[:3]:

                diagnoses.append(
                    Diagnosis(
                        rank=int(item.get("rank", 1)),
                        diagnosis=str(item.get("diagnosis", "Unknown")),
                        icd10_code=str(item.get("icd10_code", "UNKNOWN")),
                        explanation=str(item.get("explanation", "")),
                    )
                )

        return DiagnoseResponse(diagnoses=diagnoses)

    except Exception as e:

        print("FATAL ERROR:", e)

        return DiagnoseResponse(
            diagnoses=[
                Diagnosis(
                    rank=1,
                    diagnosis="Error fallback",
                    icd10_code="UNKNOWN",
                    explanation=str(e),
                )
            ]
        )