import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time as t

# IMPORT LOAD_DOTENV FUNCTION FROM DOTENV MODULE.
from dotenv import load_dotenv

from database import SessionLocal, UserToken
import datetime


# LOADS THE .ENV FILE THAT RESIDES ON THE SAME LEVEL AS THE SCRIPT.
load_dotenv(dotenv_path="stuff.env")

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
scope = 'user-top-read playlist-modify-public'

sp_oauth = SpotifyOAuth(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, scope=scope, cache_path=None)


# get top five tracks from all users
def get_top_five_tracks():
    
    all_song_ids = []
    
    session = SessionLocal()
    users = session.query(UserToken).all()

    
    for user in users:
        if user.user_id == '999571176923861092':
            continue
        # if neccessary, refresh token
        if int(user.expires_at) < int(t.time()):
            token_info = sp_oauth.refresh_access_token(user.refresh_token)
            user.access_token = token_info['access_token']
            user.expires_at = token_info['expires_at']
            session.commit()
        
        sp = spotipy.Spotify(auth=user.access_token)
        
        try:
            results = sp.current_user_top_tracks(limit=5, time_range='short_term')
            print('Top 5 tracks for user', sp.current_user()['display_name'])
        except spotipy.SpotifyException as e:
            print('An error occurred:', e)
            continue
            
        for idx, item in enumerate(results['items']):
            print(idx+1, item['name'], '//', item['artists'][0]['name'])
            # add song id to list
            all_song_ids.append(item['id'])
            
    session.close()
    return all_song_ids

def create_playlist():
    all_song_ids = get_top_five_tracks()
    
    session = SessionLocal()
    user = session.query(UserToken).filter(UserToken.user_id == '999571176923861092').first()
    # if neccessary, refresh token
    if int(user.expires_at) < int(t.time()):
        token_info = sp_oauth.refresh_access_token(user.refresh_token)
        user.access_token = token_info['access_token']
        user.expires_at = token_info['expires_at']
        session.commit()
        
    sp = spotipy.Spotify(auth=user.access_token)
    
    # get user id in spotify
    user_id = sp.current_user()['id']
    
    # get the current date
    current_date = datetime.date.today()
    
    # get the first day of the current month
    first_day_of_current_month = current_date.replace(day=1)
    
    # get the last day of the previous month
    last_day_of_previous_month = first_day_of_current_month - datetime.timedelta(days=1)
    
    # get the name of the previous month
    previous_month_name = last_day_of_previous_month.strftime('%B')
    
    # create playlist
    playlist = sp.user_playlist_create(user_id, previous_month_name, public=True)
    sp.playlist_add_items(playlist['id'], all_song_ids)
    
    # print the link to the playlist
    print('Playlist link:', playlist['external_urls']['spotify'])
    
    print('Playlist created successfully')
    session.close()

create_playlist()