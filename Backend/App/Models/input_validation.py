from pydantic import BaseModel

class Player(BaseModel):
    name: str

class Teams(BaseModel):
    team_1: str
    team_2: str