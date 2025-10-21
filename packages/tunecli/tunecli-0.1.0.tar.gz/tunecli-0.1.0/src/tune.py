import click
from spotify_client import SpotifyClient
from rich import print

spotify = SpotifyClient()

@click.group()
def cli():
    """🎶 TuneCLI - Control Spotify from your terminal"""
    pass

@cli.command()
@click.argument("query", required=True)
def play(query):
    print(query)
    print(spotify.play_track(query))

@cli.command()
def pause():
    spotify.pause()
    print("⏸️  Paused")

@cli.command()
def resume():
    spotify.resume()
    print("▶️  Resumed")

@cli.command()
def next():
    spotify.next_track()
    print("⏭️  Skipped")

@cli.command()
def previous():
    spotify.previous_track()
    print("⏮️  Previous track")

@cli.command()
def current():
    print(spotify.current())

@cli.command()
def devices():
    print(spotify.devices())

if __name__ == "__main__":
    cli()
