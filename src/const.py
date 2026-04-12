"""Constants for Zidoo component."""

import dataclasses
import logging
from dataclasses import dataclass, field, fields
from enum import Enum, StrEnum

from ucapi.media_player import MediaClass
from ucapi.media_player import MediaContentType as MediaContent

_LOGGER = logging.getLogger(__package__)


@dataclass
class MediaSearchFilter:
    """Search filter for search media command."""

    media_classes: list[str] | None
    artist: str | None
    album: str | None


class ZidooSensors(str, Enum):
    """Sensors."""

    SENSOR_AUDIO_STREAM = "sensor_audio_stream"
    SENSOR_SUBTITLE_STREAM = "sensor_subtitle_stream"
    SENSOR_VIDEO_INFO = "sensor_video_info"
    SENSOR_AUDIO_INFO = "sensor_audio_info"
    # SENSOR_VOLUME = "sensor_volume"
    # SENSOR_VOLUME_MUTED = "sensor_volume_muted"


class ZidooSelects(str, Enum):
    """Selects."""

    SELECT_AUDIO_STREAM = "select_audio_stream"
    SELECT_SUBTITLE_STREAM = "select_subtitle_stream"


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


@dataclass
class MediaEntry:
    """Media entry for browsing media."""

    title: str
    media_id: str
    media_type: MediaContent | str
    media_class: MediaClass | None = field(default=None)

    def __post_init__(self):
        """Apply default values on missing fields."""
        for attribute in fields(self):
            # If there is a default and the value of the field is none we can assign a value
            if (
                not isinstance(attribute.default, dataclasses.MISSING.__class__)
                and getattr(self, attribute.name) is None
            ):
                setattr(self, attribute.name, attribute.default)


class ZidooUrls(str, Enum):
    """Predefined urls."""

    ALL = "zidoo://videos/all"
    FAVORITES = "zidoo://videos/favorites"
    WATCHING = "zidoo://videos/watching"
    MOVIES = "zidoo://videos/movies"
    TV_SHOWS = "zidoo://videos/tvshows"
    SD = "zidoo://videos/sd"
    BLURAY = "zidoo://videos/bluray"
    UHD = "zidoo://videos/4k"
    VIDEO_3D = "zidoo://videos/3d"
    CHILDREN = "zidoo://videos/children"
    RECENT = "zidoo://videos/recent"
    UNWATCHED = "zidoo://videos/unwatched"
    OTHER = "zidoo://videos/other"
    MUSIC = "zidoo://music/songs"
    ALBUMS = "zidoo://music/albums"
    ARTISTS = "zidoo://music/artists"
    PLAYLISTS = "zidoo://music/playlists"
    FILES = "zidoo://files/main"
    SHARES = "zidoo://files/share"


# Movie Player search keys
ZVIDEO_FILTER_TYPES: dict[ZidooUrls, int] = {
    ZidooUrls.ALL: 0,
    ZidooUrls.FAVORITES: 1,
    ZidooUrls.WATCHING: 2,
    ZidooUrls.MOVIES: 3,
    ZidooUrls.TV_SHOWS: 4,
    ZidooUrls.SD: 5,
    ZidooUrls.BLURAY: 6,
    ZidooUrls.UHD: 7,
    ZidooUrls.VIDEO_3D: 8,
    ZidooUrls.CHILDREN: 9,
    ZidooUrls.RECENT: 10,
    ZidooUrls.UNWATCHED: 11,
    ZidooUrls.OTHER: 12,
    # ?"dolby": 13
}

ZIDOO_MEDIA_ENTRIES: list[MediaEntry] = [
    MediaEntry(title="Favorites", media_id=ZidooUrls.FAVORITES.value, media_type=MediaContent.VIDEO),
    MediaEntry(title="Latest", media_id=ZidooUrls.RECENT.value, media_type=MediaContent.VIDEO),
    MediaEntry(title="Watching", media_id=ZidooUrls.WATCHING.value, media_type=MediaContent.VIDEO),
    MediaEntry(title="SD", media_id=ZidooUrls.SD.value, media_type=MediaContent.VIDEO),
    MediaEntry(title="Disc", media_id=ZidooUrls.BLURAY.value, media_type=MediaContent.VIDEO),
    MediaEntry(title="UHD", media_id=ZidooUrls.UHD.value, media_type=MediaContent.VIDEO),
    MediaEntry(title="3D", media_id=ZidooUrls.VIDEO_3D.value, media_type=MediaContent.VIDEO),
    MediaEntry(title="Kids", media_id=ZidooUrls.CHILDREN.value, media_type=MediaContent.VIDEO),
    MediaEntry(title="Unwatched", media_id=ZidooUrls.UNWATCHED.value, media_type=MediaContent.VIDEO),
    MediaEntry(title="Other", media_id=ZidooUrls.OTHER.value, media_type=MediaContent.VIDEO),
    MediaEntry(title="All", media_id=ZidooUrls.ALL.value, media_type=MediaContent.VIDEO),
    MediaEntry(title="Movies", media_id=ZidooUrls.MOVIES.value, media_type=MediaContent.MOVIE),
    MediaEntry(title="TV Shows", media_id=ZidooUrls.TV_SHOWS.value, media_type=MediaContent.TV_SHOW),
    MediaEntry(title="Music", media_id=ZidooUrls.MUSIC.value, media_type=MediaContent.MUSIC),
    MediaEntry(title="Albums", media_id=ZidooUrls.ALBUMS.value, media_type=MediaContent.ALBUM),
    MediaEntry(title="Artists", media_id=ZidooUrls.ARTISTS.value, media_type=MediaContent.ARTIST),
    MediaEntry(title="Playlists", media_id=ZidooUrls.PLAYLISTS.value, media_type=MediaContent.PLAYLIST),
    MediaEntry(title="Files", media_id=ZidooUrls.FILES.value, media_type=MediaContent.URL),
    MediaEntry(title="Network files", media_id=ZidooUrls.SHARES.value, media_type=MediaContent.URL),
]

ZDEFAULT_SHORTCUTS = [
    ZidooUrls.WATCHING,
    ZidooUrls.ALL,
    ZidooUrls.RECENT,
    ZidooUrls.MOVIES,
    ZidooUrls.TV_SHOWS,
    ZidooUrls.ALBUMS,
    ZidooUrls.ARTISTS,
    ZidooUrls.MUSIC,
]


ZCONTENT_ITEM_TYPE: dict[int, MediaContent] = {
    0: MediaContent.URL,  # folder
    1: MediaContent.MUSIC,  # music
    2: MediaContent.VIDEO,  # video
    # 3: MediaType.IMAGE,  # image
    # 4: 'text',
    # 5: 'apk',
    # 6: 'pdf',
    # 7: 'document',
    # 8: 'spreadsheet',
    # 9: 'presentation',
    # 10: 'web',
    # 11: 'archive' ,
    # 12: 'other'
    1000: MediaContent.URL,  # hhd
    1001: MediaContent.URL,  # usb
    1002: MediaContent.URL,  # usb
    1003: MediaContent.URL,  # tf
    # 1004: MediaContent.URL,  # nfs
    # 1005: MediaContent.URL,  # smb
    1006: MediaContent.URL,
    1007: MediaContent.URL,
    1008: MediaContent.URL,
}

ZCONTENT_ITEM_CLASS: dict[MediaContent, MediaClass] = {
    MediaContent.URL: MediaClass.DIRECTORY,
    MediaContent.MUSIC: MediaClass.MUSIC,
    MediaContent.VIDEO: MediaClass.VIDEO,
}

# ZCONTENT_ITEM_CLASS = {
#     0: MediaClass.DIRECTORY,  # folder
#     1: MediaClass.MUSIC,  # music
#     2: MediaClass.VIDEO,  # video
#     3: MediaClass.IMAGE,  # image
#     # 4: 'text',
#     # 5: 'apk',
#     # 6: 'pdf',
#     # 7: 'document',
#     # 8: 'spreadsheet',
#     # 9: 'presentation',
#     # 10: 'web',
#     # 11: 'archive' ,
#     # 12: 'other'
#     1000: MediaClass.DIRECTORY,  # hhd
#     1001: MediaClass.DIRECTORY,  # usb
#     1002: MediaClass.DIRECTORY,  # usb
#     1003: MediaClass.DIRECTORY,  # tf
#     # 1004: MediaContent.URL,  # nfs
#     # 1005: MediaContent.URL,  # smb
#     1006: MediaClass.DIRECTORY,
#     1007: MediaClass.DIRECTORY,
#     1008: MediaClass.DIRECTORY,
# }

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


ZCMD_STATUS = "getPlayStatus"


class ZKEYS(StrEnum):
    """List of available keys."""

    ZKEY_BACK = "Key.Back"
    ZKEY_CANCEL = "Key.Cancel"
    ZKEY_HOME = "Key.Home"
    ZKEY_UP = "Key.Up"
    ZKEY_DOWN = "Key.Down"
    ZKEY_LEFT = "Key.Left"
    ZKEY_RIGHT = "Key.Right"
    ZKEY_OK = "Key.Ok"
    ZKEY_SELECT = "Key.Select"
    ZKEY_STAR = "Key.Star"
    ZKEY_POUND = "Key.Pound"
    ZKEY_DASH = "Key.Dash"
    ZKEY_MENU = "Key.Menu"
    ZKEY_MEDIA_PLAY = "Key.MediaPlay"
    ZKEY_MEDIA_STOP = "Key.MediaStop"
    ZKEY_MEDIA_PAUSE = "Key.MediaPause"
    ZKEY_MEDIA_NEXT = "Key.MediaNext"
    ZKEY_MEDIA_PREVIOUS = "Key.MediaPrev"
    ZKEY_NUM_0 = "Key.Number_0"
    ZKEY_NUM_1 = "Key.Number_1"
    ZKEY_NUM_2 = "Key.Number_2"
    ZKEY_NUM_3 = "Key.Number_3"
    ZKEY_NUM_4 = "Key.Number_4"
    ZKEY_NUM_5 = "Key.Number_5"
    ZKEY_NUM_6 = "Key.Number_6"
    ZKEY_NUM_7 = "Key.Number_7"
    ZKEY_NUM_8 = "Key.Number_8"
    ZKEY_NUM_9 = "Key.Number_9"
    ZKEY_USER_A = "Key.UserDefine_A"
    ZKEY_USER_B = "Key.UserDefine_B"
    ZKEY_USER_C = "Key.UserDefine_C"
    ZKEY_USER_D = "Key.UserDefine_D"
    ZKEY_MUTE = "Key.Mute"
    ZKEY_VOLUME_UP = "Key.VolumeUp"
    ZKEY_VOLUME_DOWN = "Key.VolumeDown"
    ZKEY_POWER_ON = "Key.PowerOn"
    ZKEY_MEDIA_BACKWARDS = "Key.MediaBackward"
    ZKEY_MEDIA_FORWARDS = "Key.MediaForward"
    ZKEY_INFO = "Key.Info"
    ZKEY_RECORD = "Key.Record"
    ZKEY_PAGE_UP = "Key.PageUP"
    ZKEY_PAGE_DOWN = "Key.PageDown"
    ZKEY_SUBTITLE = "Key.Subtitle"
    ZKEY_AUDIO = "Key.Audio"
    ZKEY_REPEAT = "Key.Repeat"
    ZKEY_MOUSE = "Key.Mouse"
    ZKEY_POPUP_MENU = "Key.PopMenu"
    ZKEY_APP_MOVIE = "Key.movie"
    ZKEY_APP_MUSIC = "Key.music"
    ZKEY_APP_PHOTO = "Key.photo"
    ZKEY_APP_FILE = "Key.file"
    ZKEY_LIGHT = "Key.light"
    ZKEY_RESOLUTION = "Key.Resolution"
    ZKEY_POWER_REBOOT = "Key.PowerOn.Reboot"
    ZKEY_POWER_OFF = "Key.PowerOn.Poweroff"
    ZKEY_POWER_STANDBY = "Key.PowerOn.Standby"
    ZKEY_PICTURE_IN_PICTURE = "Key.Pip"
    ZKEY_SCREENSHOT = "Key.Screenshot"
    ZKEY_APP_SWITCH = "Key.APP.Switch"


ZCONTENT_VIDEO = "Video Player"
ZCONTENT_MUSIC = "Music Player"
ZCONTENT_NONE = None

ZVIDEO_SEARCH_TYPES = {
    # "all": -1,    # combined results
    MediaContent.VIDEO: 0,  # all movies tvshows and collections
    MediaContent.MOVIE: 1,
    MediaContent.TV_SHOW: 2,
    MediaContent.PLAYLIST: 3,
}

ZMUSIC_SEARCH_TYPES = {MediaContent.MUSIC: 0, MediaContent.ALBUM: 1, MediaContent.ARTIST: 2, MediaContent.PLAYLIST: 3}

"""File System devicce type names"""
ZDEVICE_FOLDER = 1000
ZDEVICE_NAMES = {
    1000: "hhd",
    1001: "usb",
    1002: "usb",
    1003: "tf",
    1004: "nfs",
    1005: "smb",
}

# ZFILETYPE_NAMES = {
#     0: "folder",
#     1: "music",
#     2: "movie",
#     3: "Image",
#     4: "txt",
#     5: "apk",
#     6: "pdf",
#     7: "doc",
#     8: "xls",
#     9: "ppt",
#     10: "web",
#     11: "zip",
#     # default: "other",
# }

ZTYPE_MIMETYPE = {
    "image": 3,
    "video": 2,
    "audio": 2,  # 1 is Music Player but upnp needs dms server
    "other": 0,
    "default": 4,
    "application": 4,
}
ZUPNP_SERVERNAME = "zidoo-rc"

ZMEDIA_TYPE_ARTIST = "artist"
ZMEDIA_TYPE_ALBUM = "album"
ZMEDIA_TYPE_PLAYLIST = "playlist"

ZMUSIC_IMAGETYPE = {0: 0, 1: 1, 2: 0, 3: 0, 4: 1}
ZMUSIC_IMAGETARGET = {0: 16, 1: 16, 2: 32, 3: 16, 4: 32}
ZMUSIC_PLAYLISTTYPE = {
    ZMEDIA_TYPE_ARTIST: 3,
    ZMEDIA_TYPE_ALBUM: 4,
    ZMEDIA_TYPE_PLAYLIST: 5,
}
