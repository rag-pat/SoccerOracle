from fastapi import APIRouter
from Backend.App.Utils.fetch_data import league_standings

router = APIRouter(prefix="/standings", tags=["standings"])

@router.get("/")
async def get_standings():
    return league_standings()