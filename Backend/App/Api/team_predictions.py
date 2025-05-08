from fastapi import APIRouter, HTTPException
from Backend.App.Utils.fetch_data import latest_H2H, recent_matches
from Backend.App.Models.models import TeamsRequest
from Backend.App.Ml_Models.team_predictions import TeamDataProcessor

router = APIRouter(prefix="/team_predictions", tags=["team_predictions"])

@router.post("/predict")
async def get_team_predictions(request: TeamsRequest):
    try:
        data = TeamDataProcessor(
            team_name=request.team1,
            opponent_name=request.team2,
            league_name=request.league
        )
        
        # Get all predictions first to avoid multiple API calls
        shots_predictions = data.train_shots_model()
        possession_prediction = data.train_possession_model()
        passes_predictions = data.train_passes_model()
        fouls_prediction = data.train_fouls_model()

        if not all([shots_predictions, possession_prediction, passes_predictions, fouls_prediction]):
            raise HTTPException(status_code=404, detail="Not enough data to make predictions")

        return {
            "shots": {
                "total": shots_predictions['total']['0'] if shots_predictions else None,
                "on_target": shots_predictions['on_target']['0'] if shots_predictions else None,
                "off_target": shots_predictions['off_target']['0'] if shots_predictions else None
            },
            "possession": possession_prediction['0'] if possession_prediction else None,
            "passes": {
                "total": passes_predictions['total']['0'] if passes_predictions else None,
                "accuracy": passes_predictions['accuracy']['0'] if passes_predictions else None
            },
            "fouls": fouls_prediction['0'] if fouls_prediction else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))