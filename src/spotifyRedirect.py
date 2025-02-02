from flask import Flask, request, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth
# IMPORT THE OS MODULE.
import os

from database import SessionLocal, UserToken

# IMPORT LOAD_DOTENV FUNCTION FROM DOTENV MODULE.
from dotenv import load_dotenv
load_dotenv(dotenv_path="stuff.env")

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
scope = 'user-top-read playlist-modify-public'


app = Flask(__name__)

sp_oauth = SpotifyOAuth(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, scope=scope, cache_path=None)

@app.route("/")
def index():
    return "Hello World"

@app.route("/callback")
def callback():
    session = SessionLocal()
    code = request.args.get('code')
    user_id = request.args.get('state')
    token_info = sp_oauth.get_access_token(code, check_cache=False)
    
    
    # Add user to database
    user_token = UserToken(user_id=user_id, access_token=token_info['access_token'], refresh_token=token_info['refresh_token'], token_type=token_info['token_type'], expires_in=token_info['expires_in'], scope=token_info['scope'], expires_at=token_info['expires_at'])
    session.add(user_token)
    session.commit()
    session.close()
    return "Success"

if __name__ == "__main__":
    app.run(port=8888, debug=True, host='192.168.1.99')