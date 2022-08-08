# from pprint import pprint
from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from decouple import config

API_USERNAME = config('SPOTIPY_CLIENT_ID')
API_KEY = config('SPOTIPY_CLIENT_SECRET')
API_REDIRECT_URI = config('SPOTIPY_REDIRECT_URI')
TOKEN = config("TOKEN")

# Scraping Billboard 100
date = input("Which year do you want to travel to? Type date in this format YYYY-MM-DD: ")
url = "https://www.billboard.com/charts/hot-100/" + date
response = requests.get(url)
top_100_songs_web_page = response.text

soup = BeautifulSoup(top_100_songs_web_page, "html.parser")
track_titles = soup.select("li ul li h3")
song_names = [track.getText().replace("\n", "").replace("\t", "") for track in track_titles]

# Spotify Authentication
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri=API_REDIRECT_URI,
        client_id=API_USERNAME,
        client_secret=API_KEY,
        show_dialog=True,
        cache_path="token.txt"
    )
)
user_id = sp.current_user()["id"]
print(user_id)

# Searching Spotify for songs by title
song_uris = []
year = date.split('-')[0]
for song in song_names:
    try:
        desired_track = sp.search(q=f"track:{song} year:{year}", type="track")
        uri = desired_track['tracks']['items'][0]['uri']
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

# Creating a new private playlist in Spotify
new_playlist = sp.user_playlist_create(user=user_id, name=f"{date} Billboard 100", public=False)

# Adding songs found into the new playlist
sp.playlist_add_items(playlist_id=new_playlist["id"], items=song_uris)
