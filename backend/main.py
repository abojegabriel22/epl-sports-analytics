
from datetime import date
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.app.prediction_service import predict_match, AVAILABLE_TEAMS


app = FastAPI(
    title="EPL Sports Analytics API",
    description="API for EPL team performance analysis and match predictions.",
    version="1.0.0"
)


# Allow requests from the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://dts-project-group-17.netlify.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
STANDINGS_FILE = PROJECT_ROOT / "datasets" / "team_performance.csv"


class PredictionRequest(BaseModel):
    home_team: str = Field(min_length=1, description="Home team")
    away_team: str = Field(min_length=1, description="Away team")
    prediction_date: date = Field(description="Date of the predicted match")


@app.get("/")
def home():
    return {
        "message": "Welcome to the EPL Sports Analytics API",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "EPL API is running successfully"
    }


@app.get("/teams")
def get_teams():
    return {
        "total_teams": len(AVAILABLE_TEAMS),
        "teams": AVAILABLE_TEAMS
    }


@app.get("/standings")
def get_standings():
    """Return the latest calculated EPL league table."""

    if not STANDINGS_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                "Team standings file was not found. "
                "Run backend/app/team_performance.py first."
            )
        )

    try:
        table = pd.read_csv(STANDINGS_FILE)
        table = table.where(pd.notna(table), None)

        return {
            "status": "success",
            "total_teams": len(table),
            "season": "2026/2027",
            "data_through": "2026-10-25",
            "standings": table.to_dict(orient="records")
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Could not load team standings: {str(error)}"
        )


@app.post("/predict")
def make_prediction(request: PredictionRequest):
    try:
        result = predict_match(
            home_team=request.home_team,
            away_team=request.away_team,
            prediction_date=request.prediction_date.strftime("%Y-%m-%d")
        )

        return {
            "status": "success",
            "message": "Match prediction generated successfully",
            "prediction": result
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(error)}"
        )


@app.get("/api-info")
def api_info():
    return {
        "project": "EPL Sports Analytics",
        "version": "1.0.0",
        "features": [
            "Team performance analysis",
            "League standings",
            "Match outcome prediction",
            "Machine learning models"
        ],
        "models": [
            "Logistic Regression",
            "Random Forest"
        ],
        "available_endpoints": {
            "home": "/",
            "health": "/health",
            "teams": "/teams",
            "standings": "/standings",
            "prediction": "/predict",
            "api_info": "/api-info",
            "documentation": "/docs"
        },
        "endpoints": [
            "/",
            "/health",
            "/teams",
            "/standings",
            "/predict",
            "/api-info",
            "/docs"
        ]
    }
