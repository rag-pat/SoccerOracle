from pydantic import BaseModel
from typing import Optional

# =========================================
#               Team Stats
# =========================================

class H2H(BaseModel):
    team_1: str
    team_2: str

    total_games: int
    home_games: int
    away_games: int

    wins: int
    draws: int
    loses: int

class H2HStats(BaseModel):
    team_1: str
    team_2: str

    total_shots: int
    on_target_shots: int
    off_target_shots: int

    fouls: int
    corner_kicks: int
    offsides: int
    possession: int
    
    yellow_cards: int
    red_cards: int

    total_passes: int
    pass_accuracy: int

class ThreeMatches(BaseModel):
    team_1: str
    team_2: str

    total_shots: int
    on_target_shots: int
    off_target_shots: int

    fouls: int
    corner_kicks: int
    offsides: int
    possession: int
    
    yellow_cards: int
    red_cards: int

    total_passes: int
    pass_accuracy: int

# =========================================
#              Player Stats
# =========================================
class StatsBase(BaseModel):
    games_appearances: int
    games_minutes_played: int
    passes_total: int
    passes_key: int
    passes_accuracy: float
    tackles_total: int
    tackles_blocks: int
    tackles_interceptions: int
    duels_total: int
    duels_won: int
    dribbles_attempts: int
    dribbles_success: int
    fouls_drawn: int
    fouls_committed: int
    cards_yellow: int
    cards_red: int

class GoalkeeperStats(StatsBase):
    goals_conceded: int
    goals_saved: int

class FieldPlayerStats(StatsBase):
    goals_total: int
    goals_assists: int

class PlayerStats(BaseModel):
    name: str
    position: str
    stats: Optional[GoalkeeperStats] = None
    stats_field: Optional[FieldPlayerStats] = None