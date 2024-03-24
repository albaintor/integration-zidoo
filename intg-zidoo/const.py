"""Constants for Zidoo component."""

import logging

from ucapi.media_player import MediaType

_LOGGER = logging.getLogger(__package__)

DOMAIN = "zidoo"
DATA_ZIDOO_CONFIG = "zidoo_config"
VERSION = "1.1.1"
DATA = "data"
UPDATE_TRACK = "update_track"
UPDATE_LISTENER = "update_listener"

MANUFACTURER = "Zidoo"

CLIENTID_PREFIX = "home-assistant"
CLIENTID_NICKNAME = "Home Assistant"

CONF_SHORTCUT = "shortcut_json"
CONF_POWERMODE = "powermode"

SUBTITLE_SERVICE = "set_subtitle"
AUDIO_SERVICE = "set_audio"
BUTTON_SERVICE = "send_key"

# Triggers
EVENT_TURN_ON = "zidoo.turn_on"
EVENT_TURN_OFF = "zidoo.turn_off"

MEDIA_TYPE_FILE = "file"

ZSHORTCUTS = [
    {"name": "FAVORITES", "path": "favorite", "type": MediaType.VIDEO},
    {"name": "LATEST", "path": "recent", "type": MediaType.VIDEO, "default": True},
    {"name": "WATCHING", "path": "watching", "type": MediaType.VIDEO},
    {"name": "SD", "path": "sd", "type": MediaType.VIDEO},
    {"name": "DISC", "path": "bluray", "type": MediaType.VIDEO},
    {"name": "UHD", "path": "4k", "type": MediaType.VIDEO},
    {"name": "3D", "path": "3d", "type": MediaType.VIDEO},
    {"name": "KIDS", "path": "children", "type": MediaType.VIDEO},
    {"name": "UNWATCHED", "path": "unwatched", "type": MediaType.VIDEO},
    {"name": "OTHER", "path": "other", "type": MediaType.VIDEO},
    {"name": "ALL", "path": "all", "type": MediaType.VIDEO},
    {"name": "MOVIES", "path": "movie", "type": MediaType.MOVIE, "default": True},
    {"name": "TV SHOWS", "path": "tvshow", "type": MediaType.TVSHOW, "default": True},
    {"name": "MUSIC", "path": "music", "type": MediaType.MUSIC, "default": True},
    {"name": "ALBUMS", "path": "album", "type": MediaType.MUSIC},
    {"name": "ARTISTS", "path": "artist", "type": MediaType.MUSIC},
    {"name": "PLAYLISTS", "path": "playlist", "type": MediaType.MUSIC},
]
ZDEFAULT_SHORTCUTS = ["recent", "movie", "tvshow"]


ZCONTENT_ITEM_TYPE = {
    0: MEDIA_TYPE_FILE,  # folder
    1: MediaType.MUSIC,  # music
    2: MediaType.VIDEO,  # video
    # 3: MediaType.IMAGE,  # image
    # 4: 'text', # 5: 'apk', # 6: 'pdf', # 7: 'document', # 8: 'spreadsheet', # 9: 'presentation', # 10: 'web', # 11: 'archive' ,  # 12: 'other'
    1000: MEDIA_TYPE_FILE,  # hhd
    1001: MEDIA_TYPE_FILE,  # usb
    1002: MEDIA_TYPE_FILE,  # usb
    1003: MEDIA_TYPE_FILE,  # tf
    # 1004: MediaType.URL,  # nfs
    # 1005: MediaType.URL,  # smb
    1006: MEDIA_TYPE_FILE,
    1007: MEDIA_TYPE_FILE,
    1008: MEDIA_TYPE_FILE,
}

# ZTYPE_MEDIA_CLASS = {
#     ZTYPE_VIDEO: MediaClass.VIDEO,
#     ZTYPE_MOVIE: MediaClass.MOVIE,
#     ZTYPE_COLLECTION: MediaClass.MOVIE,
#     ZTYPE_TV_SHOW: MediaClass.TV_SHOW,
#     ZTYPE_TV_SEASON: MediaClass.SEASON,
#     ZTYPE_TV_EPISODE: MediaClass.TRACK,  # MediaClass.EPISODE, # no episode images with zidoo
#     6: MediaClass.TRACK,  # Other
#     7: MediaClass.TRACK,  # Dummy for +1
# }

# ZTYPE_MEDIA_TYPE = {
#     ZTYPE_VIDEO: MediaType.VIDEO,
#     ZTYPE_MOVIE: MediaType.MOVIE,
#     ZTYPE_COLLECTION: MediaType.MOVIE,
#     ZTYPE_TV_SHOW: MediaType.TVSHOW,
#     ZTYPE_TV_SEASON: MediaType.SEASON,
#     ZTYPE_TV_EPISODE: MediaType.EPISODE,  # no episode images with zidoo
#     ZTYPE_OTHER: MediaType.TRACK,
#     7: MediaType.TRACK,  # Dummy for +1
# }
