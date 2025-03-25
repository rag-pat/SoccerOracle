from fastapi import APIRouter
from ..Utils.fetch_data import player_season_stats, player_recent_matches
from ..Models.models import PlayerRequest
from ..Ml_Models.player_predictions import PlayerDataProcessor

router = APIRouter(prefix="/player_predictions", tags=["player_predictions"])


@router.post("/recent")
async def get_player_recent_matches(request: PlayerRequest):
    data = PlayerDataProcessor(request)
    return {
        "goals": data.train_goals_model()['0'],
        "assists": data.train_assists_model()['0'],
        "dribbles": data.train_dribbles_model()['0'],
        "passes": data.train_passes_model()['0'],
        "tackles": data.train_tackles_model()['0']
    }