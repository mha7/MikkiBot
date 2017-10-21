import os
from configparser import ConfigParser

""" This file simply loads and store all information needed for the bot. """

# Reading Config File
config = ConfigParser()
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
CONFIG_PATH = os.path.join(PROJECT_ROOT, 'credentials.ini')
config.read(CONFIG_PATH)

# BOT'S INFO ========================================
OWNER_ID = config.get('Admin', 'OWNER_ID')

CLIENT_ID = config.get('Discord Bot Credentials', 'CLIENT_ID')
CLIENT_TOKEN = config.get('Discord Bot Credentials', 'CLIENT_TOKEN')
CLIENT_SECRET = config.get('Discord Bot Credentials', 'CLIENT_SECRET')
CLIENT_PREFIX = config.get('Discord Bot Credentials', 'CLIENT_PREFIX')
CLIENT_USERNAME = config.get('Discord Bot Credentials', 'CLIENT_USERNAME')

# ===================================================
# GOOGLE'S YOUTUBE API CREDENTIALS / CONFIGS ========

YOUTUBE_API_KEY = 'AIzaSyAYtxPCOm3vuyLLp8LHa6gD1W5QFbXTTg8'
YOUTUBE_CLIENT_ID = '660526081696-ug8ibhu3mciscd9tnn4fdhp0i9b3118n.apps.googleusercontent.com'
YOUTUBE_CLIENT_SECRET = 'MKOVqCjE0BEsZUjr3pnpFfNF'
YOUTUBE_DEFAULT_SEARCH_RETURNS = config.getint('Youtube Search Config', 'YOUTUBE_DEFAULT_SEARCH_RETURNS')
YOUTUBE_MAX_SEARCH_RETURNS = config.getint('Youtube Search Config', 'YOUTUBE_MAX_SEARCH_RETURNS')

# ===================================================
# TWITCH's NEW API CREDENTIALS ======================

TWITCH_CLIENT_ID = config.get('Twitch API Credentials', 'TWITCH_CLIENT_ID')
TWITCH_CLIENT_SECRET = config.get('Twitch API Credentials', 'TWITCH_CLIENT_SECRET')


# ===================================================
# YOUTUBE_DL CONFIGS ================================

YOUTUBE_DL_CONFIGS = {
    'nocheckcertificate': 'True',
    'default_search': 'auto',
    'quiet': True,
    'format': 'bestaudio/best',
    'noplaylist': True,
    'prefer-ffmpeg': True
}

MUSIC_VOLUME_DEFAULT = config.getfloat('Music Config', 'MUSIC_VOLUME_DEFAULT')
# ===================================================
# SOUNDCLOUD CREDENTIALS / CONFIGS ==================

# SoundCloud stop giving out API Keys, so empty for now

# ===================================================
# SMUG IMAGES INITIALIZATION ========================

SMUG_LIST = []
for path, subdirs, files in os.walk(r'images/smug'):
    for filename in files:
        SMUG_LIST.append(filename)

SMUG_LIST_SIZE = len(SMUG_LIST)
# ===================================================

# LINK IMAGES INITIALIZATION ========================

LINK_LIST = []
for f_path, f_sub_dirs, f_files in os.walk(r'images/link'):
    for f_filename in f_files:
        LINK_LIST.append(f_filename)

LINK_LIST_SIZE = len(LINK_LIST)

# RIP IMAGES INITIALIZATION =========================

RIP_LIST = []
for r_path, r_sub_dirs, r_files in os.walk(r'images/rip'):
    for r_filename in r_files:
        RIP_LIST.append(r_filename)

RIP_LIST_SIZE = len(RIP_LIST)
