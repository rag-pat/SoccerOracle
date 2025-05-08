import pandas as pd
from xgboost import XGBRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

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

    def _train_model(self, df, target_col, model_type='xgb'):
        x = df.drop(columns=[target_col])
        y = df[target_col]

        if df.shape[0] < 2:
            return None

        # Use the first sample as a test case
        X_test = x.iloc[:1]
        y_test = y.iloc[:1]
        X_train = x.iloc[1:]
        y_train = y.iloc[1:]

        if model_type == 'linear':
            model = LinearRegression()
        else:
            model = XGBRegressor(objective='reg:squarederror', n_estimators=100, random_state=42)

        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)

        # Create a single prediction dictionary
        predictions = {
            "0": {
                "actual": int(y_test.values[0]),
                "predicted": round(float(y_pred[0]))
            }
        }

        return predictions



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
    



    def train_goals_model(self):
        df = self.prepare_goals_df()
        return self._train_model(df, target_col='goals_total', model_type='xgb')

    def train_assists_model(self):
        df = self.prepare_assists_df()
        return self._train_model(df, target_col='assists', model_type='xgb')

    def train_dribbles_model(self):
        df = self.prepare_dribbles_df()
        return self._train_model(df, target_col='dribbles_success', model_type='xgb')

    # Use Linear Regression (more linear)
    def train_passes_model(self):
        df = self.prepare_passes_df()
        return self._train_model(df, target_col='passes_total', model_type='linear')

    def train_tackles_model(self):
        df = self.prepare_tackles_df()
        return self._train_model(df, target_col='tackles_total', model_type='linear')