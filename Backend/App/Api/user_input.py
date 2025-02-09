from fastapi import FastAPI
from Models.input_validation import Player, Teams

app = FastAPI()

@app.post("/player-name/", response_model=Player)
def get_player_name():
    pass

@app.post("/team-names", response_model=Teams)
def get_team_names(user_input: Teams):
    pass