import requests
from creds import api_key
from ids import get_player_id, get_league_id, get_team_id

BASE_URL = "https://v3.football.api-sports.io"

headers = {
    "x-rapidapi-key": api_key,
    "x-rapidapi-host": "v3.football.api-sports.io"
}


def player_recent_matches(player_name, team_name, league_name, season=2023):
    """
    Get statistics for a player's last three games.
    
    Args:
        player_name (str): Name of the player
        league_name (str): Name of the league
        season (int): Season year (default: 2023)
    
    Returns:
        list: List of player statistics for last three games or None if error occurs
    """
    # First get league ID and player information
    league_id = get_league_id(league_name)
    if not league_id:
        print(f"Error: Could not find league ID for '{league_name}'")
        return None
    
    player_info = get_player_id(player_name, team_name, league_name, season)
    if not player_info:
        print(f"Error: Could not find player ID for '{player_name}'")
        return None
        
    player_id, player_name, position = player_info
    team_id = get_team_id(team_name, league_name, season)

    def get_team_matches(team_id, team_name):
        url = f"{BASE_URL}/fixtures"
        params = {
            "team": team_id,
            "season": season,
            "status": "FT"  # Only finished matches
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"Error fetching matches for {team_name}: {response.status_code}")
            return []

        matches_data = response.json()
        matches = matches_data.get("response", [])
        
        if not matches:
            print(f"No matches found for {team_name} in the {season} season")
            return []
            
        # Sort matches by date (newest first) and take last 3
        matches.sort(key=lambda x: x["fixture"]["date"], reverse=True)
        matches = matches[:5]
        
        return [match["fixture"]["id"] for match in matches]
    
    team_matches = get_team_matches(team_id, team_name)
    player_stats = []

    for match_id in team_matches:
        stats_url = f"{BASE_URL}/fixtures/players"
        stats_params = {"fixture": match_id}

        stats_response = requests.get(stats_url, headers=headers, params=stats_params)
        if stats_response.status_code != 200:
            print(f"Error fetching match stats: {stats_response.status_code}")
            continue

        stats_data = stats_response.json()
        print(stats_data)
        # Find player stats in the response
        for team in stats_data.get("response", []):
            for player in team.get("players", []):
                if player["player"]["id"] == player_id:
                    stats = player["statistics"][0]
                    
                    if position == "Goalkeeper":
                        match_stats = {
                            "games": {
                                "appearances": 1 if stats["games"]["minutes"] > 0 else 0,
                                "minutes_played": stats["games"]["minutes"]
                            },
                            "goals": {
                                "conceded": stats["goals"].get("conceded", 0),
                                "saves": stats["goals"].get("saves", 0)
                            },
                            "passes": {
                                "total": stats["passes"].get("total", 0),
                                "key": stats["passes"].get("key", 0),
                                "accuracy": stats["passes"].get("accuracy", 0)
                            },
                            "tackles": {
                                "total": stats["tackles"].get("total", 0),
                                "blocks": stats["tackles"].get("blocks", 0),
                                "interceptions": stats["tackles"].get("interceptions", 0)
                            },
                            "duels": {
                                "total": stats["duels"].get("total", 0),
                                "won": stats["duels"].get("won", 0)
                            },
                            "dribbles": {
                                "attempts": stats["dribbles"].get("attempts", 0),
                                "success": stats["dribbles"].get("success", 0)
                            },
                            "fouls": {
                                "drawn": stats["fouls"].get("drawn", 0),
                                "committed": stats["fouls"].get("committed", 0)
                            },
                            "cards": {
                                "yellow": stats["cards"].get("yellow", 0),
                                "red": stats["cards"].get("red", 0)
                            }
                        }
                    else:
                        match_stats = {
                            "games": {
                                "appearances": 1 if stats["games"]["minutes"] > 0 else 0,
                                "minutes_played": stats["games"]["minutes"]
                            },
                            "goals": {
                                "total": stats["goals"].get("total", 0),
                                "assists": stats["goals"].get("assists", 0)
                            },
                            "passes": {
                                "total": stats["passes"].get("total", 0),
                                "key": stats["passes"].get("key", 0),
                                "accuracy": stats["passes"].get("accuracy", 0)
                            },
                            "tackles": {
                                "total": stats["tackles"].get("total", 0),
                                "blocks": stats["tackles"].get("blocks", 0),
                                "interceptions": stats["tackles"].get("interceptions", 0)
                            },
                            "duels": {
                                "total": stats["duels"].get("total", 0),
                                "won": stats["duels"].get("won", 0)
                            },
                            "dribbles": {
                                "attempts": stats["dribbles"].get("attempts", 0),
                                "success": stats["dribbles"].get("success", 0)
                            },
                            "fouls": {
                                "drawn": stats["fouls"].get("drawn", 0),
                                "committed": stats["fouls"].get("committed", 0)
                            },
                            "cards": {
                                "yellow": stats["cards"].get("yellow", 0),
                                "red": stats["cards"].get("red", 0)
                            }
                        }
                    player_stats.append(match_stats)

    return player_stats








def recent_matches(team_1, team_2, league):
    """Fetch last 3 matches for each team with detailed statistics."""
    team_1_id = get_team_id(team_1, league)
    team_2_id = get_team_id(team_2, league)

    if not team_1_id or not team_2_id:
        print(f"Error: Could not find team IDs for '{team_1}' or '{team_2}'")
        return {team_1: [], team_2: []}

    def get_team_matches(team_id, team_name):
        url = f"{BASE_URL}/fixtures"
        params = {
            "team": team_id,
            "season": 2023,
            "status": "FT"  # Only finished matches
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"Error fetching matches for {team_name}: {response.status_code}")
            return []

        matches_data = response.json()
        matches = matches_data.get("response", [])
        
        if not matches:
            print(f"No matches found for {team_name} in the 2023 season")
            return []
            
        # Sort matches by date (newest first) and take last 3
        matches.sort(key=lambda x: x["fixture"]["date"], reverse=True)
        matches = matches[:5]
        team_matches = []

        for match in matches:
            match_id = match["fixture"]["id"]
            
            # Get match statistics
            stats_url = f"{BASE_URL}/fixtures/statistics"
            stats_params = {"fixture": match_id}
            
            stats_response = requests.get(stats_url, headers=headers, params=stats_params)
            if stats_response.status_code != 200:
                print(f"Error fetching stats for match {match_id}: {stats_response.status_code}")
                continue

            stats_data = stats_response.json()
            # Debug: Print the full stats_data to see its structure
            print(f"\nStats data for match {match_id}:")
            print(stats_data)
            
            if not stats_data.get("response"):
                print(f"No statistics available for match {match_id}")
                continue

            # Debug: Print the teams data to verify we're getting the right teams
            home_stats = stats_data["response"][0]["statistics"]
            away_stats = stats_data["response"][1]["statistics"]
            print(f"\nHome team stats: {home_stats}")
            print(f"Away team stats: {away_stats}")
            
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
                        # Debug: Print the stat being processed
                        print(f"Processing stat {name}: {value}")
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
                "result": "W" if our_team["winner"] else ("L" if opponent_team["winner"] else "D"),
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