# IMPORT DISCORD.PY. ALLOWS ACCESS TO DISCORD'S API.
import base64
from datetime import date, datetime, timedelta, time
import random
import discord
from discord import app_commands
from database import SessionLocal, UserToken

import time as t
# import cogwatch
# from cogwatch import Watcher
import concurrent.futures
import yaml
import retry

import spotipy
from spotipy.oauth2 import SpotifyOAuth

# IMPORTS EXTENSIONS FOR COMMANDS
from discord.ext import commands, tasks


# IMPORT THE OS MODULE.
import os

# IMPORT LOAD_DOTENV FUNCTION FROM DOTENV MODULE.
from dotenv import load_dotenv

# IMPORT LOGGING

import logging
import requests

# LOADS THE .ENV FILE THAT RESIDES ON THE SAME LEVEL AS THE SCRIPT.
load_dotenv(dotenv_path="stuff.env")

# GRAB THE API TOKEN FROM THE .ENV FILE.
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# GETS THE CLIENT OBJECT FROM DISCORD.PY. CLIENT IS SYNONYMOUS WITH BOT.
intents = discord.Intents.default()
bot = discord.Client(intents=intents, owner_id = 612398278209962017)
tree = app_commands.CommandTree(bot)


logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
scope = 'user-top-read playlist-modify-public'

sp_oauth = SpotifyOAuth(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, scope=scope, cache_path=None)

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user.name}')
    
    
@tree.command(name="login", description="connect your spotify account to the bot")
async def login(ctx):
    
    auth_url = sp_oauth.get_authorize_url(state=str(ctx.user.id), check_cache=False)

    # check if user already exists in database
    session = SessionLocal()
    user = session.query(UserToken).filter(UserToken.user_id == str(ctx.user.id)).first()
    session.close()
    if user:
        await ctx.response.send_message(f"You have already connected your spotify account to the bot. If you want to reconnect, click this link: {auth_url}", ephemeral=True)
        return
    
    await ctx.response.send_message(f'Please fill out this google form: https://forms.gle/9fd2gdK2WWU4xdN97, then please login to Spotify: {auth_url}', ephemeral=True)
    
@tree.command(name="listpeople", description="show the list of people who have connected their spotify account to the bot")
async def listpeople(ctx):
    session = SessionLocal()
    users = session.query(UserToken).all()
    session.close()
    if len(users) == 0:
        await ctx.response.send_message("No one has connected their spotify account to the bot")
    else:
        user_list = ""
        for user in users:
            username = await bot.fetch_user(int(user.user_id))
            user_list += f"{username}\n"
        await ctx.response.send_message(user_list)
        
@tree.command(name="toptracks", description="show the top tracks of the user for the month")
async def toptracks(ctx):
    session = SessionLocal()
    print(ctx.user.id)
    user = session.query(UserToken).filter(UserToken.user_id == str(ctx.user.id)).first()
    print(user.access_token)
    session.close()
    if user is None:
        await ctx.response.send_message("You have not connected your spotify account to the bot", ephemeral=True)
    else:
        sp = spotipy.Spotify(auth=user.access_token)
        top_tracks = sp.current_user_top_tracks(limit=5, time_range='short_term')
        track_list = ""
        for track in top_tracks['items']:
            track_list += f"{track['name']} by {track['artists'][0]['name']}\n"
        await ctx.response.send_message(track_list)

# EXECUTES THE BOT WITH THE SPECIFIED TOKEN. DON'T REMOVE THIS LINE OF CODE JUST CHANGE THE "DISCORD_TOKEN" PART TO YOUR DISCORD BOT TOKEN
bot.run(DISCORD_TOKEN)
