import pandas as pd

from ..Utils.fetch_data import player_season_stats, player_recent_matches
from ..Utils.ids import get_season_year
from ..Models.models import PlayerRequest

class PlayerDataProcessor:
    def __init__(self, player_info: PlayerRequest):
        self.player_info = player_info
        self.recent_matches = player_recent_matches(
            player_info.player_name,
            player_info.team_name,
            player_info.league_name,
            5,
            get_season_year()
        )

        print(self.recent_matches)


    def prepare_goals_df(self):
        return pd.DataFrame([{
            'minutes_played': m['games']['minutes_played'] or 0,
            'totalshots': m['goals']['totalshots'] or 0,
            'shotsongoal': m['goals']['shotsongoal'] or 0,
            'passes_total': m['passes']['total'] or 0,
            'dribbles_attempts': m['dribbles']['attempts'] or 0,
            'dribbles_success': m['dribbles']['success'] or 0,
            'goals_total': m['goals']['total'] or 0
        } for m in self.recent_matches])

    def prepare_assists_df(self):
        return pd.DataFrame([{
            'minutes_played': m['games']['minutes_played'] or 0,
            'passes_total': m['passes']['total'] or 0,
            'passes_accuracy': int(m['passes']['accuracy']) if m['passes']['accuracy'] else 0,
            'dribbles_attempts': m['dribbles']['attempts'] or 0,
            'dribbles_success': m['dribbles']['success'] or 0,
            'totalshots': m['goals']['totalshots'] or 0,
            'assists': m['goals']['assists'] or 0
        } for m in self.recent_matches])

    def prepare_dribbles_df(self):
        return pd.DataFrame([{
            'dribbles_attempts': m['dribbles']['attempts'] or 0,
            'minutes_played': m['games']['minutes_played'] or 0,
            'totalshots': m['goals']['totalshots'] or 0,
            'passes_total': m['passes']['total'] or 0,
            'passes_accuracy': int(m['passes']['accuracy']) if m['passes']['accuracy'] else 0,
            'dribbles_success': m['dribbles']['success'] or 0
        } for m in self.recent_matches])

    def prepare_passes_df(self):
        return pd.DataFrame([{
            'minutes_played': m['games']['minutes_played'] or 0,
            'passes_accuracy': int(m['passes']['accuracy']) if m['passes']['accuracy'] else 0,
            'dribbles_attempts': m['dribbles']['attempts'] or 0,
            'totalshots': m['goals']['totalshots'] or 0,
            'dribbles_success': m['dribbles']['success'] or 0,
            'passes_total': m['passes']['total'] or 0
        } for m in self.recent_matches])

    def prepare_tackles_df(self):
        return pd.DataFrame([{
            'minutes_played': m['games']['minutes_played'] or 0,
            'interceptions': m['tackles']['interceptions'] or 0,
            'dribbles_attempts': m['dribbles']['attempts'] or 0,
            'dribbles_success': m['dribbles']['success'] or 0,
            'fouls_committed': m['fouls']['committed'] or 0,
            'tackles_total': m['tackles']['total'] or 0
        } for m in self.recent_matches])