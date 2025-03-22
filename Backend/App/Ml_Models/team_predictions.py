import pandas as pd

from ..Utils.fetch_data import H2H_stats, latest_H2H, recent_matches
from ..Utils.ids import get_season_year
from ..Models.models import TeamsRequest

class TeamDataProcessor:
    def __init__(self, team_name, opponent_name, league_name):
        self.team_name = team_name
        self.opponent_name = opponent_name
        self.league_name = league_name
        self.h2h_alltime = H2H_stats(team_name, opponent_name, league_name)
        self.h2h_latest = latest_H2H(team_name, opponent_name, league_name)
        self.recent_matches = recent_matches(team_name, opponent_name, league_name, 5)[team_name]
        
    def goals(self):
        data = pd.DataFrame([{
            'goals_scored': self.extract_goals(m['score'], self.team_name),
            'goals_conceded': self.extract_goals(m['score'], m['opponent']),
            'shots_total': m['stats']['shots_total'],
            'shots_on_target': m['stats']['shots_on_target'],
            'ball_possession': float(m['stats']['ball_possession'].strip('%')),
            'passes_total': m['stats']['passes_total'],
            'passes_accuracy': m['stats']['passes_accuracy']
        } for m in self.recent_matches])
    
    def shots(self):
        data = pd.DataFrame([{
            'shots_total': m['stats']['shots_total'],
            'shots_on_target': m['stats']['shots_on_target'],
            'shots_off_target': m['stats']['shots_off_target'],
            'ball_possession': float(m['stats']['ball_possession'].strip('%')),
            'passes_total': m['stats']['passes_total']
        } for m in self.recent_matches])

    def fouls(self):
        data = pd.DataFrame([{
            'fouls': m['stats']['fouls'],
            'yellow_cards': m['stats']['yellow_cards'],
            'red_cards': m['stats']['red_cards'],
            'ball_possession': float(m['stats']['ball_possession'].strip('%'))
        } for m in self.recent_matches])

    def corners(self):
        data = pd.DataFrame([{
            'corners': m['stats']['corners'],
            'ball_possession': float(m['stats']['ball_possession'].strip('%')),
            'shots_total': m['stats']['shots_total']
        } for m in self.recent_matches])

    def possesion(self):
        data = pd.DataFrame([{
            'ball_possession': float(m['stats']['ball_possession'].strip('%')),
            'passes_total': m['stats']['passes_total'],
            'passes_accuracy': m['stats']['passes_accuracy']
        } for m in self.recent_matches])
    
    def passes(self):
        data = pd.DataFrame([{
            'passes_total': m['stats']['passes_total'],
            'passes_accuracy': m['stats']['passes_accuracy'],
            'ball_possession': float(m['stats']['ball_possession'].strip('%'))
        } for m in self.recent_matches])

    @staticmethod
    def extract_goals(score_str, team):
        # Extract goals based on which team is the target
        try:
            home_goals, away_goals = map(int, score_str.split('-'))
            return home_goals if team in score_str else away_goals
        except:
            return None