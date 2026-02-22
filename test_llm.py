import sys
import os

sys.path.append(os.path.abspath("."))

from src.llm import ask_llm

result = ask_llm(
    "Fever, dry cough, shortness of breath",
    "COVID-19 protocol description..."
)

print(result)