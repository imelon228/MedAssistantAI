# src/llm.py

import os
from openai import OpenAI

client = OpenAI(
    base_url="https://hub.qazcode.ai/v1",
    api_key=os.getenv("LLM_API_KEY")
)

def ask_llm(symptoms: str, context: str):

    prompt = f"""
Верни JSON строго в формате:

{{
  "diagnoses": [
    {{
      "rank": 1,
      "diagnosis": "название",
      "icd10_code": "код",
      "explanation": "краткое объяснение"
    }}
  ]
}}

Симптомы:
{symptoms}

Протоколы:
{context}
"""

    response = client.chat.completions.create(
    model="oss-120b",  
    messages=[
        {"role": "system", "content": "Ты строгий медицинский ассистент. Отвечай только JSON."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.2,
    response_format={"type": "json_object"}  
)

    return response.choices[0].message.content