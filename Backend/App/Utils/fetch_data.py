import requests
from fuzzywuzzy import process

API_KEY = "46ee824f034e65c62e6efc27bc34c0c1"
BASE_URL = "https://v3.football.api-sports.io"

headers = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "v3.football.api-sports.io"
}

def test_connection():
    """Check if the API connection is working."""
    url = f"{BASE_URL}/status"
    response = requests.get(url, headers=headers)
    print(response.status_code, response.json())

def response_data(response):
    if response.status_code == 200:
        data = response.json()
        print("Full Response:", data)
        if data["response"]:
            print("\n League Standings Found!")
        else:
            print("\n No standings available for this league & season.")
    else:
        print(f" Error: {response.status_code}, {response.text}")




def get_league_id(league_name):
    """Fetch league ID for a specific league."""
    url = f"{BASE_URL}/leagues"
    params = {"search": league_name}
    
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        leagues = data.get("response", [])
        
        if leagues:
            # Get all league names and find best match
            choices = [l["league"]["name"] for l in leagues]
            best_match, _ = process.extractOne(league_name, choices)
            print(f"League matched: {best_match}")
            return next(l["league"]["id"] for l in leagues if l["league"]["name"] == best_match)
        else:
            print(f"No league found with name '{league_name}'")
            return None
    else:
        print(f"Error fetching leagues: {response.status_code}, {response.text}")
        return None

def get_team_id(team_name, league_name, season=2023):
    """Fetch team ID for a given team name."""
    league_id = get_league_id(league_name)
    if not league_id:
        return None

    url = f"{BASE_URL}/teams"
    params = {
        "league": league_id,
        "season": season
    }

    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        teams = data.get("response", [])
        
        if teams:
            # Get all team names and find best match
            choices = [t["team"]["name"] for t in teams]
            best_match, _ = process.extractOne(team_name, choices)
            print(f"Team matched: {best_match}")
            return next(t["team"]["id"] for t in teams if t["team"]["name"] == best_match)
        else:
            print(f"No teams found in league '{league_name}'")
            return None
    else:
        print(f"Error fetching teams: {response.status_code}, {response.text}")
        return None

def get_player_id(player_name, team_name, league_name, season=2023):
    """Fetch player ID using team squad information."""
    team_id = get_team_id(team_name, league_name, season)
    
    if not team_id:
        print(f"Error: Could not find team ID for '{team_name}'")
        return None
        
    url = f"{BASE_URL}/players/squads"
    params = {"team": team_id}
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"Error fetching squad data: {response.status_code}")
        return None
        
    data = response.json()
    players = data["response"][0]["players"]
    
    # Find closest matching player name
    player_names = [p["name"] for p in players]
    best_match, score = process.extractOne(player_name, player_names)
    if score < 60:  # Threshold for matching
        print(f"No close match found for player '{player_name}'")
        return None
    
    print(f"Player matched: {best_match}")
    player_data = next(p for p in players if p["name"] == best_match)
    return player_data["id"], best_match, player_data["position"]



def league_standings():
    """Fetch league standings for a specific league and season."""
    url = f"{BASE_URL}/standings"

    leagues = {
        "Premier League": {"league": "39", "season": "2023"},
        "LaLiga": {"league": "140", "season": "2023"},
        "SerieA": {"league": "135", "season": "2023"},
        "Bundesliga": {"league": "78", "season": "2023"},
    }

    all_leagues = {league: {"standings": []} for league in leagues}

    for league_name, params in leagues.items():
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            teams = data.get("response", [])

            if teams:
                standings = teams[0]["league"]["standings"][0]
                
                all_leagues[league_name]["standings"] = [
                    {
                        "rank": team["rank"],
                        "name": team["team"]["name"],
                        "matches_played": team["all"]["played"],
                        "wins": team["all"]["win"],
                        "draws": team["all"]["draw"],
                        "losses": team["all"]["lose"],
                        "goals_for": team["all"]["goals"]["for"],
                        "goals_against": team["all"]["goals"]["against"],
                        "goal_diff": team["goalsDiff"],
                        "points": team["points"],
                        "last_five": team["form"],
                        "standing": team.get("description", "Regular"),
                    }
                    for team in standings[:20]
                ]
            else:
                print(f"No standings found for league '{league_name}'")
        else:
            print(f"Error fetching league data: {response.status_code}, {response.text}")

    return all_leagues


def H2H_stats(team_1, team_2, league):
    """Fetch H2H stats between two teams."""
    team_1_id = get_team_id(team_1, league)
    team_2_id = get_team_id(team_2, league)

    if not team_1_id or not team_2_id:
        print(f"Error: Could not find team IDs for '{team_1}' or '{team_2}'")
        return None

    url = f"{BASE_URL}/fixtures/headtohead"
    params = {"h2h": f"{team_1_id}-{team_2_id}"}

    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        print("Error fetching data")
        return None

    data = response.json()
    fixtures = data.get("response", [])

    stats = {
        "total_games": len(fixtures),
        "home_games": 0,
        "away_games": 0,
        "wins_team_1": 0,
        "wins_team_2": 0,
        "draws": 0
    }

    for match in fixtures:
        home_team = match["teams"]["home"]["id"]
        away_team = match["teams"]["away"]["id"]
        home_winner = match["teams"]["home"]["winner"]
        away_winner = match["teams"]["away"]["winner"]

        if home_team == team_1_id:
            stats["home_games"] += 1
            if home_winner:
                stats["wins_team_1"] += 1
            elif away_winner:
                stats["wins_team_2"] += 1
            else:
                stats["draws"] += 1
        elif away_team == team_1_id:
            stats["away_games"] += 1
            if away_winner:
                stats["wins_team_1"] += 1
            elif home_winner:
                stats["wins_team_2"] += 1
            else:
                stats["draws"] += 1

    return stats

def latest_H2H(team_1, team_2, league):
    """Fetch the latest H2H match stats between two teams in a given league."""
    team_1_id = get_team_id(team_1, league)
    team_2_id = get_team_id(team_2, league)

    if not team_1_id or not team_2_id:
        print(f"Error: Could not find team IDs for '{team_1}' or '{team_2}' in '{league}'")
        return None

    url = f"{BASE_URL}/fixtures/headtohead"
    params = {"h2h": f"{team_1_id}-{team_2_id}"}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        print(f"Error fetching data: {response.status_code}, {response.text}")
        return None

    data = response.json()
    fixtures = data.get("response", [])

    if not fixtures:
        print(f"No recent matches found for '{team_1}' vs '{team_2}' in '{league}'")
        return None

    latest_match = fixtures[0]  # Get the most recent match
    match_id = latest_match["fixture"]["id"]

    # Fetch match statistics
    stats_url = f"{BASE_URL}/fixtures/statistics"
    stats_params = {"fixture": match_id}

    stats_response = requests.get(stats_url, headers=headers, params=stats_params)

    if stats_response.status_code != 200:
        print(f"Error fetching statistics for fixture {match_id}")
        return None

    stats_data = stats_response.json()
    if not stats_data.get("response"):
        print(f"No statistics available for fixture {match_id}")
        return None

    # Extract statistics
    team_1_stats = stats_data["response"][0]["statistics"]
    team_2_stats = stats_data["response"][1]["statistics"]

    def get_stat(stats, name):
        for stat in stats:
            if stat["type"] == name:
                return stat["value"]
        return 0  # Default to 0 if stat is missing

    match_stats = {
        "match_date": latest_match["fixture"]["date"],
        "final_score": {
            team_1: latest_match["score"]["fulltime"]["home"],
            team_2: latest_match["score"]["fulltime"]["away"]
        },
        "stats": {
            team_1: {
                "shots_total": get_stat(team_1_stats, "Total Shots"),
                "shots_on_target": get_stat(team_1_stats, "Shots on Goal"),
                "shots_off_target": get_stat(team_1_stats, "Shots off Goal"),
                "fouls": get_stat(team_1_stats, "Fouls"),
                "corners": get_stat(team_1_stats, "Corner Kicks"),
                "offsides": get_stat(team_1_stats, "Offsides"),
                "ball_possession": get_stat(team_1_stats, "Ball Possession"),
                "yellow_cards": get_stat(team_1_stats, "Yellow Cards"),
                "red_cards": get_stat(team_1_stats, "Red Cards"),
                "passes_total": get_stat(team_1_stats, "Total passes"),
                "passes_accuracy": get_stat(team_1_stats, "Passes accurate")
            },
            team_2: {
                "shots_total": get_stat(team_2_stats, "Total Shots"),
                "shots_on_target": get_stat(team_2_stats, "Shots on Goal"),
                "shots_off_target": get_stat(team_2_stats, "Shots off Goal"),
                "fouls": get_stat(team_2_stats, "Fouls"),
                "corners": get_stat(team_2_stats, "Corner Kicks"),
                "offsides": get_stat(team_2_stats, "Offsides"),
                "ball_possession": get_stat(team_2_stats, "Ball Possession"),
                "yellow_cards": get_stat(team_2_stats, "Yellow Cards"),
                "red_cards": get_stat(team_2_stats, "Red Cards"),
                "passes_total": get_stat(team_2_stats, "Total passes"),
                "passes_accuracy": get_stat(team_2_stats, "Passes accurate")
            }
        }
    }

    return match_stats

def recent_matches(team_1, team_2, league):
   pass

def player_season_stats(player_name, team_name, league_name, season=2023):
    """Fetch season statistics for a specific player."""
    league_id = get_league_id(league_name)
    player_info = get_player_id(player_name, team_name, league_name, season)
    
    if not league_id or not player_info:
        return None
        
    player_id, player_name, position = player_info
    
    # Get player statistics
    url = f"{BASE_URL}/players"
    params = {
        "id": player_id,
        "season": season,
        "league": league_id
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"Error fetching player stats: {response.status_code}")
        return None
        
    data = response.json()
    if not data["response"]:
        print(f"No statistics found for player {player_name}")
        return None
        
    stats = data["response"][0]["statistics"][0]
    
    # Format statistics based on position
    if position == "Goalkeeper":
        return {
            "name": player_name,
            "position": position,
            "rating": float(f"{float(stats['games'].get('rating', 0)):.2f}"),
            "games": {
                "appearances": stats["games"]["appearences"],
                "minutes_played": stats["games"]["minutes"]
            },
            "goals": {
                "conceded": stats["goals"]["conceded"],
                "saves": stats["goals"]["saves"]
            },
            "passes": {
                "total": stats["passes"]["total"],
                "key": stats["passes"]["key"],
                "accuracy": stats["passes"]["accuracy"]
            },
            "tackles": {
                "total": stats["tackles"]["total"],
                "blocks": stats["tackles"]["blocks"],
                "interceptions": stats["tackles"]["interceptions"]
            },
            "duels": {
                "total": stats["duels"]["total"],
                "won": stats["duels"]["won"]
            },
            "dribbles": {
                "attempts": stats["dribbles"]["attempts"],
                "success": stats["dribbles"]["success"]
            },
            "fouls": {
                "drawn": stats["fouls"]["drawn"],
                "committed": stats["fouls"]["committed"]
            },
            "cards": {
                "yellow": stats["cards"]["yellow"],
                "red": stats["cards"]["red"]
            }
        }
    else:
        return {
            "name": player_name,
            "position": position,
            "rating": float(f"{float(stats['games'].get('rating', 0)):.2f}"),
            "games": {
                "appearances": stats["games"]["appearences"],
                "minutes_played": stats["games"]["minutes"]
            },
            "goals": {
                "total": stats["goals"]["total"],
                "assists": stats["goals"]["assists"]
            },
            "passes": {
                "total": stats["passes"]["total"],
                "key": stats["passes"]["key"],
                "accuracy": stats["passes"]["accuracy"]
            },
            "tackles": {
                "total": stats["tackles"]["total"],
                "blocks": stats["tackles"]["blocks"],
                "interceptions": stats["tackles"]["interceptions"]
            },
            "duels": {
                "total": stats["duels"]["total"],
                "won": stats["duels"]["won"]
            },
            "dribbles": {
                "attempts": stats["dribbles"]["attempts"],
                "success": stats["dribbles"]["success"]
            },
            "fouls": {
                "drawn": stats["fouls"]["drawn"],
                "committed": stats["fouls"]["committed"]
            },
            "cards": {
                "yellow": stats["cards"]["yellow"],
                "red": stats["cards"]["red"]
            }
        }

print(player_season_stats("Erling Haaland", "Manchester City", "Premier League", 2023))

def player_recent_matches(player_name, team_name, league_name, season=2023, limit=3):
    pass