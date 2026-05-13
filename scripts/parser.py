import requests
import json

def get_steam_games(steamid, api_key):
    # Получить список игр
    url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={api_key}&steamid={steamid}&include_appinfo=1&include_played_free_games=1"
    response = requests.get(url)
    data = response.json()
    
    games = []
    for game in data['response']['games']:
        # Получить достижения для каждой игры
        achievements_url = f"http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={game['appid']}&key={api_key}&steamid={steamid}"
        achievements_response = requests.get(achievements_url)
        
        game_data = {
            'name': game.get('name', 'Unknown'),
            'playtime_hours': round(game.get('playtime_forever', 0) / 60, 1),
            'appid': game['appid']
        }
        
        # Обработка достижений
        try:
            achievements_data = achievements_response.json()
            if 'playerstats' in achievements_data and 'achievements' in achievements_data['playerstats']:
                unlocked = sum(1 for a in achievements_data['playerstats']['achievements'] if a.get('achieved', 0) == 1)
                total = len(achievements_data['playerstats']['achievements'])
                game_data['achievements'] = f"{unlocked}/{total}"
            else:
                game_data['achievements'] = "N/A"
        except:
            game_data['achievements'] = "N/A"
        
        games.append(game_data)
    
    return games
