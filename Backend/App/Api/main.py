from fastapi import FastAPI
from Backend.App.Api import standings, teams, players

app = FastAPI(
    title="Football Stats API",
    description="API for football statistics including standings, team comparisons, and player stats",
    version="1.0.0"
)

# Include all routers
app.include_router(standings.router)
app.include_router(teams.router)
app.include_router(players.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Football Stats API"}