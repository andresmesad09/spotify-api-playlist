import os

from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(override=True)

SPOTIFY_ENDPOINT = "https://api.spotify.com/v1/users/12184404201/playlists"

date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")

response = requests.get("https://www.billboard.com/charts/hot-100/" + date)

soup = BeautifulSoup(response.text, 'html.parser')
song_names_spans = soup.select("li ul li h3")
song_authors_span = soup.select("li ul li span")
song_names = [song.getText().strip() for song in song_names_spans]
song_authors = [song.getText().strip() for index, song in enumerate(song_authors_span) if index == 0 or index % 7 == 0]
song_dict = {k: v for k, v in zip(song_names, song_authors)}
# print(song_dict)

scope = ["user-library-read", "playlist-modify-private", "playlist-modify-public"]

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope=scope,
        client_id=os.environ.get("CLIENT_ID"),
        client_secret=os.environ.get("CLIENT_SECRET"),
        redirect_uri="http://127.0.0.1:9090"
    ))

user = sp.current_user()['id']
print(user)

year = datetime.strptime(date, '%Y-%m-%d').year
spotify_uris = []
for song, author in song_dict.items():
    # print(f"Looking for {song} from {author}")
    try:
        song_search = sp.search(q=f"track: {song} year: {year}", type="track")
        # song_search_object = json.loads(song_search)
        uri = song_search['tracks']['items'][0]['uri']
        spotify_uris.append(uri)
    except Exception as e:
        print(f"Song: {song} not there. Exception: {e}")
        continue

# create playlist
playlist = sp.user_playlist_create(
    user=user,
    name=f"{date} Billboard 100",
    public=True,
    description=f"Billboard 100 - Python project - {date}"
)
sp.playlist_add_items(playlist_id=playlist["id"], items=spotify_uris)
