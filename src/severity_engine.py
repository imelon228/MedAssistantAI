# src/severity_engine.py

def calculate_severity(data: dict):

    score = 0
    reasons = []

    temperature = data.get("temperature")
    systolic = data.get("systolic_bp")
    heart_rate = data.get("heart_rate")
    leukocytes = data.get("leukocytes")
    age = data.get("age")
    symptoms = [s.lower() for s in data.get("symptoms", [])]
    comorbidities = [c.lower() for c in data.get("history", [])]

    # Температура
    if temperature and temperature >= 39:
        score += 2
        reasons.append("Высокая температура")

    # Гипотония
    if systolic and systolic < 90:
        score += 3
        reasons.append("Низкое давление")

    # Тахикардия
    if heart_rate and heart_rate > 120:
        score += 2
        reasons.append("Тахикардия")

    # Судороги
    if "судороги" in symptoms:
        score += 5
        reasons.append("Судороги")

    # Потеря сознания
    if "потеря сознания" in symptoms:
        score += 5
        reasons.append("Потеря сознания")

    # Одышка
    if "одышка" in symptoms:
        score += 3
        reasons.append("Одышка")

    # Лейкоцитоз
    if leukocytes and leukocytes > 15:
        score += 2
        reasons.append("Высокий лейкоцитоз")

    # Пожилой возраст
    if age and age > 65:
        score += 2
        reasons.append("Пожилой возраст")

    # Сахарный диабет
    if "сд" in " ".join(comorbidities):
        score += 2
        reasons.append("Сахарный диабет")

    # Классификация
    if score <= 3:
        level = "stable"
    elif score <= 6:
        level = "moderate"
    else:
        level = "critical"

    return {
        "score": score,
        "level": level,
        "reasons": reasons
    }