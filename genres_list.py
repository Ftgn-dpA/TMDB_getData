import json

import requests

url = "https://api.themoviedb.org/3/genre/movie/list?language=en"
headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyZTJiNWVjN2M5NmE5Nzk1MGE1MDJlMzk1MWMzZmRkNCIsInN1YiI6IjY1ZjIzN2RlZmJlMzZmMDE4NWVmZTJjZSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.0xB5s2dJJONa7P9-W5oD5B74DgWf6bZwTiixveJ55po"
}

response = requests.get(url, headers=headers).json()
genres_dict = {genre['id']: genre['name'] for genre in response['genres']}
with open('./genres_dict.json', 'w', encoding='utf-8') as f:
    json.dump(genres_dict, f, ensure_ascii=False, indent=4)
