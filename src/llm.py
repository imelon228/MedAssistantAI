import json
from openai import OpenAI
from src.config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL


def create_client():

    if not LLM_API_KEY or not LLM_BASE_URL:
        raise ValueError("LLM_BASE_URL and LLM_API_KEY must be set")

    print(f"[LLM] Using provider: {LLM_BASE_URL}")

    return OpenAI(
        api_key=LLM_API_KEY,
        base_url=LLM_BASE_URL,
    )


client = None

try:
    client = create_client()
except Exception as e:
    print("[LLM] disabled:", e)


def ask_llm(symptoms: str, context: str):

    if client is None:
        return {"diagnoses": []}

    prompt = f"""
You are a clinical ICD-10 diagnosis system.

Symptoms:
{symptoms}

Relevant protocols:
{context}

Return ONLY valid JSON in this format:

{{
  "diagnoses": [
    {{
      "rank": 1,
      "diagnosis": "name",
      "icd10_code": "code",
      "explanation": "short reason"
    }},
    {{
      "rank": 2,
      "diagnosis": "name",
      "icd10_code": "code",
      "explanation": "short reason"
    }},
    {{
      "rank": 3,
      "diagnosis": "name",
      "icd10_code": "code",
      "explanation": "short reason"
    }}
  ]
}}

Return ONLY JSON. No text outside JSON.
"""

    try:

        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are an ICD-10 medical diagnosis AI."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
        )

        content = response.choices[0].message.content

        # parse JSON safely
        result = json.loads(content)

        return result

    except Exception as e:

        print("[LLM ERROR]", e)

        return {"diagnoses": []}