import spotipy
from spotipy.oauth2 import SpotifyOAuth

class SpotifyClient:
    def __init__(self):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id="40133dedf91e4f898373ff835d057e67",
            client_secret="95f87e493e4f4f969f43697b6fcf726f",
            redirect_uri="http://127.0.0.1:8888/callback",
            scope="user-read-playback-state user-modify-playback-state"
        ))

    def play_track(self, query):
        results = self.sp.search(q=query, type="track", limit=1)
        tracks = results['tracks']['items']
        if not tracks:
            return f"No results for '{query}'"
        track = tracks[0]
        uri = track['uri']
        self.sp.start_playback(uris=[uri])
        return f"🎵 Playing {track['name']} by {track['artists'][0]['name']}"
    
    def devices(self):
        devices = self.sp.devices()['devices']
        return devices

    def pause(self):
        self.sp.pause_playback()

    def resume(self):
        self.sp.start_playback()

    def next_track(self):
        self.sp.next_track()

    def previous_track(self):
        self.sp.previous_track()

    def current(self):
        playback = self.sp.current_playback()
        if playback and playback.get('item'):
            track = playback['item']
            return f"Now playing: {track['name']} – {track['artists'][0]['name']}"
        return "No track currently playing."
