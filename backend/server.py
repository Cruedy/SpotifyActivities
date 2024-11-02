import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, url_for, session, request, redirect, jsonify
from flask_cors import CORS
import requests
import json
import time
import pandas as pd
from dotenv import load_dotenv
import os

# App config
app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])

tempos = []
ids = []

app.secret_key = os.getenv("CLIENT_SECRET")
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'
load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def is_logged_in():
    return "token_info" in session 

@app.route('/login')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return jsonify({"auth_url": auth_url})  

@app.route('/authorize', methods=['POST'])
def authorize():
    sp_oauth = create_spotify_oauth()
    code = request.json.get('code')  # Get the authorization code from the JSON body
    token_info = sp_oauth.get_access_token(code)  # Get the token info
    session["token_info"] = token_info  # Store token info in the session
    return jsonify({"status": "success", "token": token_info['access_token']})


@app.route('/logout')
def logout():
    session.clear()  # Clear the session
    return redirect('/')

@app.route('/getTracks', methods=["GET"])
def get_all_tracks():
    if not is_logged_in():  # Check if the user is logged in
        return redirect('/login')  # Redirect to login if not logged in

    token_info = session['token_info']  # Retrieve token info from the session
    sp = spotipy.Spotify(auth=token_info['access_token'])  # Create a Spotify client
    results = []
    iter = 0
    while True:
        offset = iter * 50  # Spotify API allows retrieving 50 items at a time
        iter += 1
        curGroup = sp.current_user_saved_tracks(limit=50, offset=offset)['items']
        for item in curGroup:
            track = item['track']
            results.append(track['id'])  # Collect track IDs
        if len(curGroup) < 50:  # Break the loop if there are no more items
            break
    df = pd.DataFrame(results, columns=["ids"]) 
    df.to_csv('songs.csv', index=False)

    return redirect('/checkTempos')

@app.route('/checkTempos', methods=["GET"])
def checkTempos():
    df = pd.read_csv('songs.csv')
    for index, row in df.iterrows():
        ids.append(row['ids'])
        tempos.append(getSongTempo(row['ids']))
        print(tempos)
        print(ids)
    return jsonify({"tempos": tempos})

@app.route('/createPlaylist', methods=["GET"])
def createPlaylist(category="weight_lifting"):
    df = pd.read_csv('ranges.csv')
    matching_row = df[df['category'] == category]
    min = matching_row['min']
    max = matching_row['max']
    select_ids = []
    for i in range(len(tempos)):
        if min <= tempos[i] <= max:
            select_ids.append(ids[i])
    # create playlists
    

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri="http://localhost:3000/authorize",  # Ensure this matches your frontend redirect URI
        scope="user-library-read"  # Scopes needed for your app
    )

def get_token():
    token_valid = False
    token_info = session.get("token_info", {})
    if not token_info:
        return token_info, token_valid
    now = int(time.time())
    is_token_expired = token_info.get('expires_at') - now < 60
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