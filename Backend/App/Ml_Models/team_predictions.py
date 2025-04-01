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
    
    def _train_model(self, df, target_col, model_type='xgb'):
        x = df.drop(columns=[target_col])
        y = df[target_col]

        if df.shape[0] < 2:
            print(f"Not enough data to train the model for {target_col}")
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

        # Print results for visibility
        print(f"\n----- {target_col.upper()} [{model_type}] -----")
        print(f"Test MSE: {mse:.4f}")
        for key, pred in predictions.items():
            print(f"Actual: {pred['actual']}, Predicted: {pred['predicted']}")

        return predictions

    def goals(self):
        return pd.DataFrame([{
            'goals_scored': self.extract_goals(m['score'], self.team_name),
            'goals_conceded': self.extract_goals(m['score'], m['opponent']),
            'shots_total': m['stats']['shots_total'],
            'shots_on_target': m['stats']['shots_on_target'],
            'ball_possession': float(m['stats']['ball_possession'].strip('%')),
            'passes_total': m['stats']['passes_total'],
            'passes_accuracy': m['stats']['passes_accuracy']
        } for m in self.recent_matches])
    
    def shots(self):
        return pd.DataFrame([{
            'shots_total': m['stats']['shots_total'],
            'shots_on_target': m['stats']['shots_on_target'],
            'shots_off_target': m['stats']['shots_off_target'],
            'ball_possession': float(m['stats']['ball_possession'].strip('%')),
            'passes_total': m['stats']['passes_total']
        } for m in self.recent_matches])

    def fouls(self):
        return pd.DataFrame([{
            'fouls': m['stats']['fouls'],
            'yellow_cards': m['stats']['yellow_cards'],
            'red_cards': m['stats']['red_cards'],
            'ball_possession': float(m['stats']['ball_possession'].strip('%'))
        } for m in self.recent_matches])

    def corners(self):
        return pd.DataFrame([{
            'corners': m['stats']['corners'],
            'ball_possession': float(m['stats']['ball_possession'].strip('%')),
            'shots_total': m['stats']['shots_total']
        } for m in self.recent_matches])

    def possesion(self):
        return pd.DataFrame([{
            'ball_possession': float(m['stats']['ball_possession'].strip('%')),
            'passes_total': m['stats']['passes_total'],
            'passes_accuracy': m['stats']['passes_accuracy']
        } for m in self.recent_matches])
    
    def passes(self):
        return pd.DataFrame([{
            'passes_total': m['stats']['passes_total'],
            'passes_accuracy': m['stats']['passes_accuracy'],
            'ball_possession': float(m['stats']['ball_possession'].strip('%'))
        } for m in self.recent_matches])
    
    def train_goals_model(self):
        df = self.prepare_goals_df()
        return self._train_model(df, target_col='goals_scored', model_type='xgb')
    
    def train_shots_model(self):
        df = self.prepare_shots_df()
        return self._train_model(df, target_col='shots_total', model_type='xgb')
    
    def train_fouls_model(self):
        df = self.prepare_fouls_df()
        return self._train_model(df, target_col='fouls', model_type='linear')
    
    def train_corners_model(self):
        df = self.prepare_corners_df()
        return self._train_model(df, target_col='corners', model_type='linear')
    
    def train_passes_model(self):
        df = self.prepare_passes_df()
        return self._train_model(df, target_col='passes_total', model_type='linear')
        

if __name__ == "__main__":
    # Mock team details
    team_name = "Manchester City"
    opponent_name = "Manchester United"
    league_name = "Premier Leauge"

    # Initialize processor
    processor = TeamDataProcessor(team_name, opponent_name, league_name)

    print("\n--- Testing Team Predictions ---")

    print("\n🔵 Testing Goals Model")
    goals_predictions = processor.train_goals_model()
    print(goals_predictions)

    print("\n⚽ Testing Shots Model")
    shots_predictions = processor.train_shots_model()
    print(shots_predictions)

    print("\n🟨 Testing Fouls Model")
    fouls_predictions = processor.train_fouls_model()
    print(fouls_predictions)

    print("\n🔲 Testing Corners Model")
    corners_predictions = processor.train_corners_model()
    print(corners_predictions)

    print("\n🎯 Testing Passes Model")
    passes_predictions = processor.train_passes_model()
    print(passes_predictions)