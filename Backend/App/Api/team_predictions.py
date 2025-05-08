from fastapi import APIRouter, HTTPException
from Backend.App.Utils.fetch_data import latest_H2H, recent_matches
from Backend.App.Models.models import TeamsRequest
from Backend.App.Ml_Models.team_predictions import TeamDataProcessor

router = APIRouter(prefix="/team_predictions", tags=["team_predictions"])

@router.post("/predict")
async def get_team_predictions(request: TeamsRequest):
    try:
        data_team1 = TeamDataProcessor(
            team_name=request.team_1,
            opponent_name=request.team_2,
            league_name=request.league
        )
        data_team2 = TeamDataProcessor(
            team_name=request.team_2,
            opponent_name=request.team_1,
            league_name=request.league
        )

        predictions = {
            request.team_1: {
                "shots": data_team1.train_shots_model(),
                "possession": data_team1.train_possession_model(),
                "passes": data_team1.train_passes_model(),
                "fouls": data_team1.train_fouls_model()
            },
            request.team_2: {
                "shots": data_team2.train_shots_model(),
                "possession": data_team2.train_possession_model(),
                "passes": data_team2.train_passes_model(),
                "fouls": data_team2.train_fouls_model()
            }
        }

        return predictions

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))