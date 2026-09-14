from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel


# --------------------------------------------------
# FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="Smart City Traffic Intelligence API",
    description="API for predicting high-risk traffic conditions.",
    version="1.0.0"
)


# --------------------------------------------------
# Load trained model
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent

MODEL_PATH = (
    PROJECT_DIR
    / "data"
    / "processed"
    / "random_forest_classification_model.joblib"
)

model = joblib.load(MODEL_PATH)


# --------------------------------------------------
# Input data schema
# --------------------------------------------------

class TrafficInput(BaseModel):
    temp: float
    rain_1h: float
    snow_1h: float
    clouds_all: float
    hour: int
    day_of_week: int
    day_of_month: int
    month: int
    is_weekend: bool
    weather_main: str


# --------------------------------------------------
# API endpoints
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Smart City Traffic Intelligence API",
        "status": "running"
    }


@app.post("/predict")
def predict(data: TrafficInput):

    input_data = pd.DataFrame([{
        "temp": data.temp,
        "rain_1h": data.rain_1h,
        "snow_1h": data.snow_1h,
        "clouds_all": data.clouds_all,
        "hour": data.hour,
        "day_of_week": data.day_of_week,
        "day_of_month": data.day_of_month,
        "month": data.month,
        "is_weekend": data.is_weekend,
        "weather_main": data.weather_main
    }])

    prediction = model.predict(input_data)[0]
    probability = model.predict_proba(input_data)[0][1]

    risk_label = "High Risk" if prediction == 1 else "Normal Risk"

    return {
        "prediction": int(prediction),
        "risk_level": risk_label,
        "high_risk_probability": round(float(probability), 4)
    }