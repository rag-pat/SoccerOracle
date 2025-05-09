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

    def _train_model(self, df, target_col, model_type='xgb', label=None):
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

        predictions = {
            label or "0": {
                "actual": int(y_test.values[0]),
                "predicted": round(float(y_pred[0]))
            }
        }

        return predictions

    def prepare_shots_df(self):
        return pd.DataFrame([{
            'ball_possession': int(m['stats']['ball_possession'].strip('%')),
            'passes_total': m['stats']['passes_total'],
            'passes_accuracy': m['stats']['passes_accuracy'],
            'fouls': m['stats']['fouls'],
            'corners': m['stats']['corners'],
            'shots_total': m['stats']['shots_total'],
            'shots_on_target': m['stats']['shots_on_target'],
            'shots_off_target': m['stats']['shots_off_target']
        } for m in self.recent_matches[self.team_name]])

    def prepare_possession_df(self):
        return pd.DataFrame([{
            'passes_total': m['stats']['passes_total'],
            'passes_accuracy': m['stats']['passes_accuracy'],
            'shots_total': m['stats']['shots_total'],
            'corners': m['stats']['corners'],
            'ball_possession': int(m['stats']['ball_possession'].strip('%'))
        } for m in self.recent_matches[self.team_name]])

    def prepare_passes_df(self):
        return pd.DataFrame([{
            'ball_possession': int(m['stats']['ball_possession'].strip('%')),
            'shots_total': m['stats']['shots_total'],
            'corners': m['stats']['corners'],
            'passes_total': m['stats']['passes_total'],
            'passes_accuracy': m['stats']['passes_accuracy']
        } for m in self.recent_matches[self.team_name]])

    def prepare_fouls_df(self):
        return pd.DataFrame([{
            'ball_possession': int(m['stats']['ball_possession'].strip('%')),
            'shots_total': m['stats']['shots_total'],
            'corners': m['stats']['corners'],
            'passes_total': m['stats']['passes_total'],
            'fouls': m['stats']['fouls']
        } for m in self.recent_matches[self.team_name]])

    def train_shots_model(self):
        df = self.prepare_shots_df()
        return {
            'total': self._train_model(df, target_col='shots_total', model_type='xgb', label=self.team_name),
            'on_target': self._train_model(df, target_col='shots_on_target', model_type='xgb', label=self.team_name),
            'off_target': self._train_model(df, target_col='shots_off_target', model_type='xgb', label=self.team_name)
        }

    def train_possession_model(self):
        df = self.prepare_possession_df()
        return self._train_model(df, target_col='ball_possession', model_type='linear', label=self.team_name)

    def train_passes_model(self):
        df = self.prepare_passes_df()
        return {
            'total': self._train_model(df, target_col='passes_total', model_type='linear', label=self.team_name),
            'accuracy': self._train_model(df, target_col='passes_accuracy', model_type='linear', label=self.team_name)
        }

    def train_fouls_model(self):
        df = self.prepare_fouls_df()
        return self._train_model(df, target_col='fouls', model_type='linear', label=self.team_name)