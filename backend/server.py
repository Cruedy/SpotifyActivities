import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, url_for, session, request, redirect
import json
import time
import pandas as pd
from dotenv import load_dotenv
import os

# App config
app = Flask(__name__)

app.secret_key = os.getenv("CLIENT_SECRET")
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'
load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

@app.route('/')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    print(auth_url)  # Check if the URL is generated correctly
    return redirect(auth_url)

@app.route('/authorize')
def authorize():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    return redirect("/getTracks")

@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')

@app.route('/getTracks')
def get_all_tracks():
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect('/')
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    results = []
    iter = 0
    while True:
        offset = iter * 50
        iter += 1
        curGroup = sp.current_user_saved_tracks(limit=50, offset=offset)['items']
        for idx, item in enumerate(curGroup):
            track = item['track']
            val = track['name'] + " - " + track['artists'][0]['name']
            results += [val]
        if (len(curGroup) < 50):
            break
    
    df = pd.DataFrame(results, columns=["song names"]) 
    df.to_csv('songs.csv', index=False)
    return "done"


# Checks to see if token is valid and gets a new token if not
def get_token():
    token_valid = False
    token_info = session.get("token_info", {})

    # Checking if the session already has a token stored
    if not (session.get('token_info', False)):
        token_valid = False
        return token_info, token_valid

    # Checking if token has expired
    now = int(time.time())
    is_token_expired = session.get('token_info').get('expires_at') - now < 60

    # Refreshing token if it has expired
    if (is_token_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(session.get('token_info').get('refresh_token'))

    token_valid = True
    return token_info, token_valid


def create_spotify_oauth():
    return SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=url_for('authorize', _external=True),
            scope="user-library-read")


# from flask import Flask, request, url_for, redirect, session
# from dotenv import load_dotenv
# import os
# import base64
# from requests import post, get
# import json
# import spotipy
# from spotipy.oauth2 import SpotifyOAuth
# import pandas as pd

# load_dotenv()

# client_id = os.getenv("CLIENT_ID")
# client_secret = os.getenv("CLIENT_SECRET")
# TOKEN_INFO = "token_info"

# app = Flask(__name__)

# @app.route('/playlists')
# def getUserPlaylists():
#     return {"playlist": ["song1", "song2"]}

# @app.route('/')
# def login():
#     sp_oauth = create_spotify_oauth()
#     auth_url = sp_oauth.get_authorize_url()
#     return redirect(auth_url)

# @app.route('/redirect')
# def redirect():
#     sp_oauth = create_spotify_oauth()
#     session.clear()
#     code = request.args.get('get')
#     token_info = sp_oauth.get_access_token(code)
#     session[TOKEN_INFO] = token_info
#     return 'redirect'

# def create_spotify_oauth():
#     return SpotifyOAuth(
#             client_id=client_id,
#             client_secret=client_secret,
#             redirect_uri=url_for('redirectPage', _external=True),
#             scope="user-library-read")

# def getToken():
#     auth_string = client_id + ":" + client_secret
#     auth_bytes = auth_string.encode("utf-8")
#     auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

#     url = "https://accounts.spotify.com/api/token"
#     headers = {
#         "Authorization": "Basic " + auth_base64,
#         "Content-Type": "application/x-www-form-urlencoded"
#     }
#     data = {"grant_type": "client_credentials"}
#     result = post(url, headers=headers, data=data)
#     json_result = json.loads(result.content)
#     token = json_result["access_token"]
#     return token

# def getTracks():
#     session['token_info'], authorized = getToken()
#     session.modified = True
#     if not authorized:
#         return redirect('/')
#     sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
#     results = []
#     iter = 0
#     while True:
#         offset = iter * 50
#         iter += 1
#         curGroup = sp.current_user_saved_tracks(limit=50, offset=offset)['items']
#         for idx, item in enumerate(curGroup):
#             track = item['track']
#             val = track['name'] + " - " + track['artists'][0]['name']
#             results += [val]
#         if (len(curGroup) < 50):
#             break
    
#     df = pd.DataFrame(results, columns=["song names"]) 
#     df.to_csv('songs.csv', index=False)
#     return "done"


# # def getAuthHeader(token):
# #     return {"Authorization": "Bearer " + token}

# # def getTopSongs(token):
# #     url = "https://api.spotify.com/v1/me/top/tracks"
# #     headers = getAuthHeader(token)

# # token = getToken()
# # print(token)


