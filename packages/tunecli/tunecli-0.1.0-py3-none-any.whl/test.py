import spotipy
from spotipy.oauth2 import SpotifyOAuth


sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="40133dedf91e4f898373ff835d057e67",
    client_secret="95f87e493e4f4f969f43697b6fcf726f",
    redirect_uri="http://127.0.0.1:8888/callback",
    scope="user-read-playback-state user-modify-playback-state"
))

print(sp.current_user()) 

devices = sp.devices()['devices']
print(devices)  # should list at least one active device