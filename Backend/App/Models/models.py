from pydantic import BaseModel

class TeamsRequest(BaseModel):
    team_1: str
    team_2: str
    league: str

class PlayerRequest(BaseModel):
    player_name: str
    team_name: str
    league_name: str