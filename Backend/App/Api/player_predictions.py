from fastapi import APIRouter
from ..Utils.fetch_data import player_season_stats, player_recent_matches
from ..Models.models import PlayerRequest

router = APIRouter(prefix="/player_predictions", tags=["player_predictions"])

@router.post("/season")
async def get_player_season_stats(request: PlayerRequest):
    return 0

@router.post("/recent")
async def get_player_recent_matches(request: PlayerRequest):
    return 0