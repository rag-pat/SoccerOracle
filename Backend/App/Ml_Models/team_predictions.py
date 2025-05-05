import pandas as pd
from xgboost import XGBRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

from ..Utils.fetch_data import H2H_stats, latest_H2H, recent_matches
from ..Utils.ids import get_season_year
from ..Models.models import TeamsRequest

class TeamDataProcessor:
    def __init__(self, team_name, opponent_name, league_name):
        self.team_name = team_name
        self.opponent_name = opponent_name
        self.league_name = league_name
        self.h2h_alltime = H2H_stats(
            team_name, 
            opponent_name, 
            league_name
        )
        self.h2h_latest = latest_H2H(
            team_name, 
            opponent_name, 
            league_name
        )
        self.recent_matches = recent_matches(
            team_name, 
            opponent_name, 
            league_name, 
            5
        )