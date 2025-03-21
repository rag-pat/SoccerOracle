from fastapi import APIRouter
from Backend.App.Utils.fetch_data import latest_H2H, recent_matches
from Backend.App.Models.models import TeamsRequest

router = APIRouter(prefix="/team_predictions", tags=["team_predictions"])

@router.post("/head_to_head")
async def get_head_to_head(request: TeamsRequest):
    return latest_H2H(
        request.team1,
        request.team2,
        request.league
    )

@router.post("/recent")
async def get_recent_matches(request: TeamsRequest):
    return recent_matches(
        request.team1,
        request.team2,
        request.league,
        3
    )