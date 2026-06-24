from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
from contextlib import asynccontextmanager
import os

# --- 1. Definición del Ciclo de Vida (Lifespan) ---
# Usamos lifespan para cargar el modelo y el preprocesador en memoria una sola vez al arrancar 
# el servidor, optimizando el rendimiento de cada predicción.
modelos = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Rutas relativas a los archivos .pkl
    ruta_modelo = os.path.join("entrenamiento", "models", "model.pkl")
    ruta_preprocesador = os.path.join("entrenamiento", "models", "preprocessor.pkl")
    
    # Validamos que los archivos existan
    if not os.path.exists(ruta_modelo) or not os.path.exists(ruta_preprocesador):
        raise FileNotFoundError(
            "No se encontraron los archivos 'model.pkl' o 'preprocessor.pkl' en la carpeta 'entrenamiento/models/'. "
            "Asegúrate de haber ejecutado la última celda de tu Jupyter Notebook."
        )
    
    # Cargamos el modelo y preprocesador
    print("Cargando modelo y preprocesador...")
    modelos["modelo"] = joblib.load(ruta_modelo)
    modelos["preprocesador"] = joblib.load(ruta_preprocesador)
    print("¡Modelo y preprocesador cargados exitosamente!")
    
    yield
    # Limpieza al apagar el servidor (opcional)
    modelos.clear()
    print("Servidor apagado y modelos descargados.")

# --- 2. Inicialización de FastAPI ---
app = FastAPI(
    title="API de Predicción de Burnout Estudiantil",
    description="API que utiliza un modelo de Random Forest para predecir el riesgo de burnout en base al uso de IA y hábitos de estudio.",
    version="1.0.0",
    lifespan=lifespan
)

# --- 3. Configuración de CORS ---
# Permite que el frontend (HTML/JS) que corre en tu navegador web local pueda hacer
# peticiones de red a este backend sin ser bloqueado por seguridad.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción deberías cambiar "*" por la URL de tu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 4. Esquema de Validación de Datos (Pydantic) ---
# Define de forma estricta las 14 variables de entrada que el modelo requiere.
class DatosEstudiante(BaseModel):
    Major_Category: str
    Year_of_Study: str
    Pre_Semester_GPA: float
    Weekly_GenAI_Hours: float
    Primary_Use_Case: str
    Prompt_Engineering_Skill: str
    Tool_Diversity: int
    Paid_Subscription: bool
    Traditional_Study_Hours: float
    Perceived_AI_Dependency: int
    Institutional_Policy: str
    Anxiety_Level_During_Exams: int
    Post_Semester_GPA: float
    Skill_Retention_Score: float

    # Ejemplo de datos para documentar la API interactiva (Swagger)
    model_config = {
        "json_schema_extra": {
            "example": {
                "Major_Category": "STEM",
                "Year_of_Study": "Junior",
                "Pre_Semester_GPA": 3.2,
                "Weekly_GenAI_Hours": 10.5,
                "Primary_Use_Case": "Coding_Assistance",
                "Prompt_Engineering_Skill": "Intermediate",
                "Tool_Diversity": 4,
                "Paid_Subscription": False,
                "Traditional_Study_Hours": 15.0,
                "Perceived_AI_Dependency": 5,
                "Institutional_Policy": "Allowed_With_Citation",
                "Anxiety_Level_During_Exams": 6,
                "Post_Semester_GPA": 3.4,
                "Skill_Retention_Score": 80.0
            }
        }
    }

# --- 5. Endpoints de la API ---

@app.get("/")
def read_root():
    return {
        "mensaje": "¡API de Predicción de Burnout Estudiantil en funcionamiento!",
        "documentacion": "/docs"
    }

@app.post("/predict")
def predict_burnout(datos: DatosEstudiante):
    try:
        # A. Convertir los datos de Pydantic a un diccionario
        datos_dict = datos.model_dump()
        
        # B. Convertir el diccionario en un DataFrame de Pandas (1 sola fila)
        # Esto es vital porque ColumnTransformer (scikit-learn) necesita los nombres de las columnas
        df_input = pd.DataFrame([datos_dict])
        
        # C. Obtener el preprocesador y modelo de la memoria
        preprocesador = modelos["preprocesador"]
        modelo = modelos["modelo"]
        
        # D. Aplicar el preprocesamiento a los datos de entrada
        X_procesado = preprocesador.transform(df_input)
        
        # E. Realizar la predicción
        prediccion = modelo.predict(X_procesado)[0]
        
        # F. Obtener probabilidades (para hacer más interactivo el frontend)
        # Devuelve las probabilidades de cada clase en el orden: modelo.classes_
        probabilidades = modelo.predict_proba(X_procesado)[0]
        probabilidades_dict = {
            clase: float(prob) 
            for clase, prob in zip(modelo.classes_, probabilidades)
        }
        
        # G. Retornar la respuesta JSON
        return {
            "prediccion": prediccion,
            "probabilidades": probabilidades_dict,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno durante la predicción: {str(e)}"
        )