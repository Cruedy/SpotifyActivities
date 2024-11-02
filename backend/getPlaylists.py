from flask import Flask, session, jsonify, redirect
import pandas as pd
import requests
import time
import os
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
import spotipy
from urllib.parse import urlencode

load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI", "http://localhost:8888/callback")  # Adjust as necessary
scope = "user-library-read"

activity_bpm = {
    "weight_lifting": [130, 150],
    "sprinting": [140, 145],
    "jogging": [120, 140],
    "Steady State Cardio": [120, 140],
    "competitive running": [170, 180],
    "walking": [120, 130],
    "power walking": [135, 145],
    "slow walking": [90, 115],
    "stair master": [120, 160],
    "warm up": [100, 140],
    "yoga": [60, 90],
    "pilates": [60, 90],
    "low intensity": [60, 90],
    "Cool Down": [60, 90],
    "Stretching":[60, 90],
    "CrossFit": [140, 180],
    "HIIT": [140, 180],
    "Zumba": [130, 170],
    "Dance": [130, 170]
}

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri="http://localhost:3000/authorize",  # Ensure this matches your frontend redirect URI
        scope="user-library-read"  # Scopes needed for your app
    )

# Checks to see if token is valid and gets a new token if not
def get_token():
    token_valid = False
    token_info = session.get("token_info", {})

    # Check if there is a token stored in the session
    if not token_info:
        return token_info, token_valid

    # Check if the token has expired
    now = int(time.time())
    is_token_expired = token_info.get('expires_at') - now < 60

    # Refresh the token if it has expired
    if is_token_expired:
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info.get('refresh_token'))

    token_valid = True
    return token_info, token_valid


def getSongTempo(id):
    print(id)
    print('iddddd')
    token_info, authorized = get_token()
    print('token got')
    session.modified = True
    if not authorized:
        return redirect('/')
    sp = spotipy.Spotify(auth=token_info['access_token'])
    url = "https://api.spotify.com/v1/audio-features/" + id
    headers = {
        "Authorization": f"Bearer {token_info['access_token']}"
    }
    response = requests.get(url, headers=headers)
    data = response.json()  
    tempo = data['tempo']
    return tempo
    
def checkTempos():
    df = pd.read_csv('songs.csv')
    for index, row in df.iterrows():
        print(row['ids'])
        print(getSongTempo(row['ids']))

checkTempos()



