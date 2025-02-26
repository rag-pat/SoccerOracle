from fastapi import APIRouter
from Backend.App.Utils.fetch_data import H2H_stats, latest_H2H, recent_matches
from Backend.App.Models.models import TeamsRequest

router = APIRouter(prefix="/teams", tags=["teams"])

@router.post("/h2h")
async def get_h2h(request: TeamsRequest):
    return H2H_stats(
        request.team_1, 
        request.team_2, 
        request.league
    )

@router.post("/h2h/latest")
async def get_latest_h2h(request: TeamsRequest):
    return latest_H2H(
        request.team_1, 
        request.team_2, 
        request.league
    )

@router.post("/recent")
async def get_recent_matches(request: TeamsRequest):
    return recent_matches(
        request.team_1, 
        request.team_2, 
        request.league, 
        3
    )