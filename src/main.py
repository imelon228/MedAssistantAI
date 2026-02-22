from fastapi import FastAPI
from src.models import DiagnoseRequest, DiagnoseResponse, Diagnosis
from src.vector_db import search_protocols
from src.llm import ask_llm
import json
from dotenv import load_dotenv
from src.severity_engine import calculate_severity
load_dotenv()
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from fastapi.middleware.cors import CORSMiddleware




app = FastAPI(
    title="Medical Diagnosis AI",
    description="Symptoms → ICD-10 diagnostic system",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="frontend"), name="static")
@app.get("/")
def serve_frontend():
    return FileResponse("frontend/index.html")

@app.post("/diagnose", response_model=DiagnoseResponse)
def diagnose(request: dict):

    try:

        # =========================
        # 1️⃣ Универсальный вход
        # =========================

        if "text" in request:
            # это evaluate.py
            symptoms = request["text"]

            age = None
            temperature = None
            systolic_bp = None
            heart_rate = None
            leukocytes = None
            history = ""

        else:
            # это frontend
            symptoms = f"""
            Жалобы: {request.get("complaints")}
            Пациент: {request.get("patient_info")}
            Витальные: {request.get("vitals")}
            Анализы: {request.get("lab_results")}
            Анамнез: {request.get("anamnesis")}
            """

            # можно потом парсить реальные значения
            age = request.get("age")
            temperature = request.get("temperature")
            systolic_bp = request.get("systolic_bp")
            heart_rate = request.get("heart_rate")
            leukocytes = request.get("leukocytes")
            history = request.get("anamnesis")

        if not symptoms.strip():
            return DiagnoseResponse(diagnoses=[])

        # =========================
        # 2️⃣ Vector search
        # =========================

        protocols = search_protocols(symptoms)

        if not protocols:
            return DiagnoseResponse(diagnoses=[])

        context = "\n\n".join(
            f"Diagnosis: {p['title']}\n"
            f"ICD10: {p['icd10_code']}\n"
            f"Text: {p['text'][:500]}"
            for p in protocols
        )

        llm_result = ask_llm(symptoms, context)

        if isinstance(llm_result, str):
            try:
                llm_result = json.loads(llm_result)
            except:
                llm_result = {}

        diagnoses = []

        llm_diagnoses = llm_result.get("diagnoses", [])

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

        # =========================
        # 3️⃣ Severity
        # =========================

        severity = calculate_severity({
            "temperature": temperature,
            "systolic_bp": systolic_bp,
            "heart_rate": heart_rate,
            "leukocytes": leukocytes,
            "age": age,
            "symptoms": symptoms,
            "history": history
        })

        emergency_data = None

        if severity["level"] == "critical":
            emergency_data = {
                "triggered": True,
                "level": "critical",
                "message": "Состояние может быть критическим",
                "call_ambulance": True,
                "ambulance_number": "103"
            }

        # =========================
        # 4️⃣ RETURN
        # =========================

        return DiagnoseResponse(
            diagnoses=diagnoses,
            severity_score=severity["score"],
            severity_level=severity["level"],
            severity_reasons=severity["reasons"],
            emergency=emergency_data
        )

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