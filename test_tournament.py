import requests

api_key = "lip_cCtQVPpg50AfVhvHAiht"
tournament_id = "your_tournament_id_here"  # Replace with a valid tournament ID
url = f"https://lichess.org/api/tournament/m45sueue"

headers = {
    "Authorization": f"Bearer {api_key}"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    tournament_info = response.json()
    print("Tournament Info:", tournament_info)
else:
    print(f"Failed to retrieve tournament: {response.status_code}")
