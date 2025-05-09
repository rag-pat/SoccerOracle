import requests
from fuzzywuzzy import process
from .creds import api_key

from .ids import get_team_id, get_league_id, get_player_id, get_team_matches, get_season_year

BASE_URL = "https://v3.football.api-sports.io"

headers = {
    "x-rapidapi-key": api_key,
    "x-rapidapi-host": "v3.football.api-sports.io"
}

def league_standings():
    """Fetch league standings for a specific league and season."""
    url = f"{BASE_URL}/standings"

    leagues = {
        "Premier League": {"league": "39", "season": f"{get_season_year()}"},
        "LaLiga": {"league": "140", "season": f"{get_season_year()}"},
        "SerieA": {"league": "135", "season": f"{get_season_year()}"},
        "Bundesliga": {"league": "78", "season": f"{get_season_year()}"},
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

    return all_leagues

def H2H_stats(team_1, team_2, league):
    """Fetch H2H stats between two teams."""
    team_1_id = get_team_id(team_1, league)
    team_2_id = get_team_id(team_2, league)

    if not team_1_id or not team_2_id:
        return {"error_code": 404, "message": "Teams not found"}

    url = f"{BASE_URL}/fixtures/headtohead"
    params = {"h2h": f"{team_1_id}-{team_2_id}"}

    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        return {"error_code": response.status_code, "message": "Error fetching data"}

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
        return {"error_code": 404, "message": "Teams not found"}

    url = f"{BASE_URL}/fixtures/headtohead"
    params = {"h2h": f"{team_1_id}-{team_2_id}"}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return {"error_code": response.status_code, "message": response.json().get("message")}

    data = response.json()
    fixtures = data.get("response", [])

    if not fixtures:
        return {"error_code": 404, "message": "No fixtures found"}

    latest_match = fixtures[0]  # Get the most recent match
    match_id = latest_match["fixture"]["id"]

    # Fetch match statistics
    stats_url = f"{BASE_URL}/fixtures/statistics"
    stats_params = {"fixture": match_id}

    stats_response = requests.get(stats_url, headers=headers, params=stats_params)

    if stats_response.status_code != 200:
        return {"error_code": stats_response.status_code, "message": stats_response.json().get("message")}

    stats_data = stats_response.json()
    if not stats_data.get("response"):
        return {"error_code": 404, "message": "No statistics found"}

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

def recent_matches(team_1, team_2, league, number_matches):
    """Fetch last 3 matches for each team with detailed statistics."""
    team_1_id = get_team_id(team_1, league)
    team_2_id = get_team_id(team_2, league)

    if not team_1_id or not team_2_id:
        return {"error_code": 404, "message": "Teams not found"}

    def get_team_matches(team_id, team_name):
        url = f"{BASE_URL}/fixtures"
        params = {
            "team": team_id,
            "season": get_season_year(),
            "status": "FT"  # Only finished matches
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            return {"error_code": response.status_code, "message": response.json().get("message")}

        matches_data = response.json()
        matches = matches_data.get("response", [])
        
        if not matches:
            return {"error_code": 404, "message": f"No matches found for {team_name}"}
            
        # Sort matches by date (newest first) and take last 3
        matches.sort(key=lambda x: x["fixture"]["date"], reverse=True)
        matches = matches[:number_matches]
        team_matches = []

        for match in matches:
            match_id = match["fixture"]["id"]
            
            # Get match statistics
            stats_url = f"{BASE_URL}/fixtures/statistics"
            stats_params = {"fixture": match_id}
            
            stats_response = requests.get(stats_url, headers=headers, params=stats_params)
            if stats_response.status_code != 200:
                return {"error_code": stats_response.status_code, "message": stats_response.json().get("message")}

            stats_data = stats_response.json()

            if not stats_data.get("response"):
                return {"error_code": 404, "message": f"No statistics found for match {match_id}"}

            # Get the teams data
            home_stats = stats_data["response"][0]["statistics"]
            away_stats = stats_data["response"][1]["statistics"]

            # Determine which team is the one we're looking for
            home_team = match["teams"]["home"]
            away_team = match["teams"]["away"]
            is_home = home_team["id"] == team_id
            
            our_team = home_team if is_home else away_team
            opponent_team = away_team if is_home else home_team
            our_score = match["goals"]["home"] if is_home else match["goals"]["away"]
            opponent_score = match["goals"]["away"] if is_home else match["goals"]["home"]

            # Get the correct stats based on home/away
            our_stats = home_stats if is_home else away_stats
            
            def get_stat(stats, name):
                for stat in stats:
                    if stat["type"] == name:
                        value = stat["value"]
                        if value is None:
                            return 0
                        if isinstance(value, str) and value.endswith('%'):
                            return value
                        return value
                return 0

            match_info = {
                "date": match["fixture"]["date"],
                "opponent": opponent_team["name"],
                "score": f"{our_score}-{opponent_score}",
                "result": "W" if our_team.get("winner") else ("L" if opponent_team.get("winner") else "D"),
                "stats": {
                    "shots_total": get_stat(our_stats, "Total Shots"),
                    "shots_on_target": get_stat(our_stats, "Shots on Goal"),
                    "shots_off_target": get_stat(our_stats, "Shots off Goal"),
                    "fouls": get_stat(our_stats, "Fouls"),
                    "corners": get_stat(our_stats, "Corner Kicks"),
                    "offsides": get_stat(our_stats, "Offsides"),
                    "ball_possession": get_stat(our_stats, "Ball Possession"),
                    "yellow_cards": get_stat(our_stats, "Yellow Cards"),
                    "red_cards": get_stat(our_stats, "Red Cards"),
                    "passes_total": get_stat(our_stats, "Total passes"),
                    "passes_accuracy": get_stat(our_stats, "Passes accurate")
                }
            }
            team_matches.append(match_info)

        return team_matches

    # Process teams independently
    results = {}
    results[team_1] = get_team_matches(team_1_id, team_1)
    results[team_2] = get_team_matches(team_2_id, team_2)

    return results

def player_season_stats(player_name, team_name, league_name, season):
    """Fetch season statistics for a specific player."""
    league_id = get_league_id(league_name)
    player_info = get_player_id(player_name, team_name, league_name, season)
    
    if not league_id or not player_info:
        return {"error_code": 404, "message": "Player or league not found"}
        
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
        return {"error_code": response.status_code, "message": response.json().get("message")}
        
    data = response.json()
    if not data["response"]:
        return {"error_code": 404, "message": "Player not found"}
        
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
                "assists": stats["goals"]["assists"],
                "totalshots": stats["shots"]["total"],
                "shotsongoal": stats["shots"]["on"]
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

def player_recent_matches(player_name, team_name, league_name, number_matches, season):
    """
    Get statistics for a player's last three games.
    
    Args:
        player_name (str): Name of the player
        league_name (str): Name of the league
        season (int): Season year (default is current year)
    
    Returns:
        list: List of player statistics for last three games or None if error occurs
    """
    # First get league ID and player information
    league_id = get_league_id(league_name)
    if not league_id:
        return {"error_code": 404, "message": "League not found"}
    
    player_info = get_player_id(player_name, team_name, league_name, season)
    if not player_info:
        return {"error_code": 404, "message": "Player not found"}
        
    player_id, player_name, position = player_info
    team_id = get_team_id(team_name, league_name, season)
    
    team_matches = get_team_matches(team_id, team_name, season, number_matches)
    player_stats = []

    for match_id in team_matches:
        stats_url = f"{BASE_URL}/fixtures/players"
        stats_params = {"fixture": match_id}

        stats_response = requests.get(stats_url, headers=headers, params=stats_params)
        if stats_response.status_code != 200:
            return {"error_code": stats_response.status_code, "message": stats_response.json().get("message")}

        stats_data = stats_response.json()

        for team in stats_data.get("response", []):
            for player in team.get("players", []):
                if player["player"]["id"] == player_id:
                    stats = player["statistics"][0]
                    
                    # Safely get minutes played with a default of 0
                    minutes_played = stats.get("games", {}).get("minutes", 0) or 0
                    
                    if position == "Goalkeeper":
                        match_stats = {
                            "games": {
                                "appearances": 1 if minutes_played > 0 else 0,
                                "minutes_played": minutes_played
                            },
                            "goals": {
                                "conceded": stats.get("goals", {}).get("conceded", 0) or 0,
                                "saves": stats.get("goals", {}).get("saves", 0) or 0
                            },
                            "passes": {
                                "total": stats.get("passes", {}).get("total", 0) or 0,
                                "key": stats.get("passes", {}).get("key", 0) or 0,
                                "accuracy": stats.get("passes", {}).get("accuracy", 0) or 0
                            },
                            "tackles": {
                                "total": stats.get("tackles", {}).get("total", 0) or 0,
                                "blocks": stats.get("tackles", {}).get("blocks", 0) or 0,
                                "interceptions": stats.get("tackles", {}).get("interceptions", 0) or 0
                            },
                            "duels": {
                                "total": stats.get("duels", {}).get("total", 0) or 0,
                                "won": stats.get("duels", {}).get("won", 0) or 0
                            },
                            "dribbles": {
                                "attempts": stats.get("dribbles", {}).get("attempts", 0) or 0,
                                "success": stats.get("dribbles", {}).get("success", 0) or 0
                            },
                            "fouls": {
                                "drawn": stats.get("fouls", {}).get("drawn", 0) or 0,
                                "committed": stats.get("fouls", {}).get("committed", 0) or 0
                            },
                            "cards": {
                                "yellow": stats.get("cards", {}).get("yellow", 0) or 0,
                                "red": stats.get("cards", {}).get("red", 0) or 0
                            }
                        }
                    else:
                        match_stats = {
                            "games": {
                                "appearances": 1 if minutes_played > 0 else 0,
                                "minutes_played": minutes_played
                            },
                            "goals": {
                                "total": stats.get("goals", {}).get("total", 0) or 0,
                                "assists": stats.get("goals", {}).get("assists", 0) or 0,
                                "totalshots": stats.get("shots", {}).get("total", 0) or 0,
                                "shotsongoal": stats.get("shots", {}).get("on", 0) or 0
                            },
                            "passes": {
                                "total": stats.get("passes", {}).get("total", 0) or 0,
                                "key": stats.get("passes", {}).get("key", 0) or 0,
                                "accuracy": stats.get("passes", {}).get("accuracy", 0) or 0
                            },
                            "tackles": {
                                "total": stats.get("tackles", {}).get("total", 0) or 0,
                                "blocks": stats.get("tackles", {}).get("blocks", 0) or 0,
                                "interceptions": stats.get("tackles", {}).get("interceptions", 0) or 0
                            },
                            "duels": {
                                "total": stats.get("duels", {}).get("total", 0) or 0,
                                "won": stats.get("duels", {}).get("won", 0) or 0
                            },
                            "dribbles": {
                                "attempts": stats.get("dribbles", {}).get("attempts", 0) or 0,
                                "success": stats.get("dribbles", {}).get("success", 0) or 0
                            },
                            "fouls": {
                                "drawn": stats.get("fouls", {}).get("drawn", 0) or 0,
                                "committed": stats.get("fouls", {}).get("committed", 0) or 0
                            },
                            "cards": {
                                "yellow": stats.get("cards", {}).get("yellow", 0) or 0,
                                "red": stats.get("cards", {}).get("red", 0) or 0
                            }
                        }
                    player_stats.append(match_stats)

    return player_stats