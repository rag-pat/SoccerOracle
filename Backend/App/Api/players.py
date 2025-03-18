from fastapi import APIRouter
from Backend.App.Utils.fetch_data import player_season_stats, player_recent_matches
from Backend.App.Models.models import PlayerRequest

router = APIRouter(prefix="/players", tags=["players"])

@router.post("/stats")
async def get_player_stats(request: PlayerRequest):
    return player_season_stats(
        request.player_name,
        request.team_name,
        request.league_name,
        request.season
    )

@router.post("/recent")
async def get_player_recent(request: PlayerRequest):
    return player_recent_matches(
        request.player_name,
        request.team_name,
        request.league_name,
        3,
    )