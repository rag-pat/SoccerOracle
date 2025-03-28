import requests
from fuzzywuzzy import process
from .creds import api_key
from datetime import datetime

BASE_URL = "https://v3.football.api-sports.io"

headers = {
    "x-rapidapi-key": api_key,
    "x-rapidapi-host": "v3.football.api-sports.io"
}

def get_season_year():
    current_date = datetime.now()
    year = current_date.year
    month = current_date.month
    
    # If the month is from July (7) to December (12), return the next year
    if month >= 7:
        return year
    # Otherwise, return the current year
    return year - 1

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
            return next(l["league"]["id"] for l in leagues if l["league"]["name"] == best_match)
        else:
            return {"error_code": response.status_code, "message": response.json().get("message")}
    else:
        return {"error_code": response.status_code, "message": response.json().get("message")}

def get_team_id(team_name, league_name, season=get_season_year()):
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
            return next(t["team"]["id"] for t in teams if t["team"]["name"] == best_match)
        else:
            return {"error_code": response.status_code, "message": response.json().get("message")}
    else:
        return {"error_code": response.status_code, "message": response.json().get("message")}

def get_player_id(player_name, team_name, league_name, season=get_season_year()):
    """Fetch player ID using team squad information."""
    team_id = get_team_id(team_name, league_name, season)
    
    if not team_id:
        return {"error_code": response.status_code, "message": response.json().get("message")}
        
    url = f"{BASE_URL}/players/squads"
    params = {"team": team_id}
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        return {"error_code": response.status_code, "message": response.json().get("message")}
        
    data = response.json()
    players = data["response"][0]["players"]
    
    # Find closest matching player name
    player_names = [p["name"] for p in players]
    best_match, score = process.extractOne(player_name, player_names)
    if score < 60:  # Threshold for matching
        return {"error_code": response.status_code, "message": response.json().get("message")}
    
    player_data = next(p for p in players if p["name"] == best_match)
    return player_data["id"], best_match, player_data["position"]

def get_team_matches(team_id, team_name, season, number_matches):
        url = f"{BASE_URL}/fixtures"
        params = {
            "team": team_id,
            "season": season,
            "status": "FT"  # Only finished matches
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            return {"error_code": response.status_code, "message": response.json().get("message")}

        matches_data = response.json()
        matches = matches_data.get("response", [])
        
        if not matches:
            return {"error_code": 404, "message": f"No matches found for {team_name}"}
            
        matches.sort(key=lambda x: x["fixture"]["date"], reverse=True)
        matches = matches[:number_matches]
        
        return [match["fixture"]["id"] for match in matches]