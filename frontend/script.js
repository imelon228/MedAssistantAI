document.addEventListener("DOMContentLoaded", () => {

    const form = document.getElementById("diagnosis-form");
    const responseContainer = document.getElementById("ai-response-container");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const formData = new FormData(form);

        const data = {
            complaints: formData.get("complaints"),
            vitals: formData.get("vitals"),
            patient_info: formData.get("patient_info"),
            lab_results: formData.get("lab_results"),
            anamnesis: formData.get("anamnesis")
        };

        try {

            responseContainer.innerHTML = "Анализируем...";

            const response = await fetch("http://127.0.0.1:8000/diagnose", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                throw new Error("Ошибка сервера");
            }

            const result = await response.json();

            renderResult(result);

        } catch (error) {
            responseContainer.innerHTML = "Ошибка соединения с сервером.";
            console.error(error);
        }
    });

    function renderResult(result) {

        if (!result.diagnoses || result.diagnoses.length === 0) {
            responseContainer.innerHTML = "Диагноз не найден.";
            return;
        }

        const diagnosis = result.diagnoses[0];

        responseContainer.innerHTML = `
            <div class="results-wrapper">
                <div class="diagnosis-header">
                    <div class="info-card">
                        <div class="card-label">Предварительный диагноз</div>
                        <div class="card-value">${diagnosis.diagnosis}</div>
                    </div>

                    <div class="info-card">
                        <div class="card-label">ICD-10</div>
                        <div class="card-value">${diagnosis.icd10_code}</div>
                    </div>
                </div>

                <div class="ai-answer">
                    <div class="ai-text">
                        ${diagnosis.explanation}
                    </div>
                </div>
            </div>
        `;
    }

});