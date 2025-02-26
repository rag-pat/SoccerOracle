from fastapi import APIRouter
from Backend.App.Utils.fetch_data import player_season_stats, player_recent_matches
from Backend.App.Models.models import PlayerRequest

router = APIRouter(prefix="/player_predictions", tags=["player_predictions"])

@router.post("/season")
async def get_player_season_stats(request: PlayerRequest):
    return player_season_stats(
        request.player, 
        request.league
    )

@router.post("/recent")
async def get_player_recent_matches(request: PlayerRequest):
    return player_recent_matches(
        request.player, 
        request.team,
        request.league, 
        3
    )
