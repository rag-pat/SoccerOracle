from team_predictions import TeamDataProcessor

def test_team_predictions():
    # Initialize the processor with two teams
    processor = TeamDataProcessor(
        team_name="Manchester City",
        opponent_name="Manchester United",
        league_name="Premier League"
    )

    # Test shots predictions
    print("\n=== Testing Shots Predictions ===")
    shots_predictions = processor.train_shots_model()
    if shots_predictions:
        print("Shots Total:", shots_predictions['total'])
        print("Shots On Target:", shots_predictions['on_target'])
        print("Shots Off Target:", shots_predictions['off_target'])

    # Test possession prediction
    print("\n=== Testing Possession Prediction ===")
    possession_prediction = processor.train_possession_model()
    if possession_prediction:
        print("Ball Possession:", possession_prediction)

    # Test passes predictions
    print("\n=== Testing Passes Predictions ===")
    passes_predictions = processor.train_passes_model()
    if passes_predictions:
        print("Passes Total:", passes_predictions['total'])
        print("Passes Accuracy:", passes_predictions['accuracy'])

    # Test fouls prediction
    print("\n=== Testing Fouls Prediction ===")
    fouls_prediction = processor.train_fouls_model()
    if fouls_prediction:
        print("Fouls:", fouls_prediction)

if __name__ == "__main__":
    test_team_predictions() 