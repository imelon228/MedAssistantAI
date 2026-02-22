from src.severity_engine import calculate_severity

test_data = {
  "symptoms": ["судороги", "одышка"],
  "temperature": 39.5,
  "systolic_bp": 80,
  "heart_rate": 130,
  "leukocytes": 18,
  "age": 70,
  "history": ["СД 2 типа"]
}

result = calculate_severity(test_data)

print(result)

assert result["level"] == "critical"