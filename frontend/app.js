document.getElementById('burnoutForm').addEventListener('submit', async (e) => {
    e.preventDefault(); // Evita que la página se recargue

    // 1. Obtener los elementos del DOM de la vista
    const placeholderView = document.getElementById('placeholderView');
    const resultView = document.getElementById('resultView');
    const btnPredict = document.querySelector('.btn-predict');
    
    // Cambiar estado del botón a cargando
    btnPredict.textContent = "Analizando...";
    btnPredict.disabled = true;

    // 2. Capturar y estructurar los datos del formulario
    const payload = {
        Major_Category: document.getElementById('Major_Category').value,
        Year_of_Study: document.getElementById('Year_of_Study').value,
        Pre_Semester_GPA: parseFloat(document.getElementById('Pre_Semester_GPA').value),
        Weekly_GenAI_Hours: parseFloat(document.getElementById('Weekly_GenAI_Hours').value),
        Primary_Use_Case: document.getElementById('Primary_Use_Case').value,
        Prompt_Engineering_Skill: document.getElementById('Prompt_Engineering_Skill').value,
        Tool_Diversity: parseInt(document.getElementById('Tool_Diversity').value),
        Paid_Subscription: document.getElementById('Paid_Subscription').checked,
        Traditional_Study_Hours: parseFloat(document.getElementById('Traditional_Study_Hours').value),
        Perceived_AI_Dependency: parseInt(document.getElementById('Perceived_AI_Dependency').value),
        Institutional_Policy: document.getElementById('Institutional_Policy').value,
        Anxiety_Level_During_Exams: parseInt(document.getElementById('Anxiety_Level_During_Exams').value),
        Post_Semester_GPA: parseFloat(document.getElementById('Post_Semester_GPA').value),
        Skill_Retention_Score: parseFloat(document.getElementById('Skill_Retention_Score').value)
    };

    try {
        // 3. Realizar la llamada HTTP POST a la API
        const response = await fetch('http://127.0.0.1:8000/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`Error en el servidor: ${response.statusText}`);
        }

        const data = await response.json();

        // 4. Renderizar los resultados si la respuesta fue exitosa
        if (data.status === 'success') {
            // Ocultar placeholder y mostrar contenedor de resultados
            placeholderView.classList.add('hidden');
            resultView.classList.remove('hidden');

            // Formatear el Badge de Burnout
            const burnoutBadge = document.getElementById('burnoutBadge');
            const burnoutValue = document.getElementById('burnoutValue');
            const resultText = document.getElementById('resultText');

            // Limpiar clases previas del badge
            burnoutBadge.className = 'badge-result';

            // Configurar color y textos según la predicción del modelo
            const prediccion = data.prediccion.toUpperCase(); // "HIGH", "MEDIUM" o "LOW"
            burnoutValue.textContent = prediccion;

            if (prediccion === 'HIGH') {
                burnoutBadge.classList.add('high');
                resultText.textContent = "Alerta: El modelo estima un nivel de estrés y burnout muy elevado. Se recomienda reducir la dependencia de la IA y buscar orientación académica/personal para reestructurar los hábitos de estudio.";
            } else if (prediccion === 'MEDIUM') {
                burnoutBadge.classList.add('medium');
                resultText.textContent = "Riesgo Moderado: El nivel de burnout es intermedio. Sería provechoso equilibrar el uso de IA con más sesiones de estudio tradicional activo y técnicas de relajación.";
            } else {
                burnoutBadge.classList.add('low');
                resultText.textContent = "Estado Saludable: El riesgo de burnout es bajo. El estudiante mantiene un buen balance en su aprendizaje y niveles de ansiedad controlados.";
            }

            // Actualizar las barras de probabilidades con una pequeña animación
            const probHigh = data.probabilidades.High * 100;
            const probMedium = data.probabilidades.Medium * 100;
            const probLow = data.probabilidades.Low * 100;

            document.getElementById('probHighText').textContent = `${probHigh.toFixed(1)}%`;
            document.getElementById('probHighFill').style.width = `${probHigh}%`;

            document.getElementById('probMediumText').textContent = `${probMedium.toFixed(1)}%`;
            document.getElementById('probMediumFill').style.width = `${probMedium}%`;

            document.getElementById('probLowText').textContent = `${probLow.toFixed(1)}%`;
            document.getElementById('probLowFill').style.width = `${probLow}%`;
        }

    } catch (error) {
        console.error('Error al consultar la API:', error);
        alert('Ocurrió un error al intentar conectarse al servidor de predicción. Asegúrate de que tu API de FastAPI esté corriendo.');
    } finally {
        // Restaurar estado del botón
        btnPredict.textContent = "Analizar Riesgo";
        btnPredict.disabled = false;
    }
});
