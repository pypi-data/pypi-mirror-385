#!/usr/bin/python3

from os import makedirs
from datetime import datetime
from urllib.parse import urlparse
from requests import get as req_get
from zipfile import ZipFile, ZIP_DEFLATED
from deezspot.models.track import Track
from deezspot.exceptions import InvalidLink
from deezspot.libutils.others_settings import supported_link, header

from os.path import (
    isdir, basename,
    join, isfile
)

def link_is_valid(link):
    netloc = urlparse(link).netloc

    if not any(
        c_link == netloc
        for c_link in supported_link
    ):
        raise InvalidLink(link)

def get_ids(link):
    parsed = urlparse(link)
    path = parsed.path
    ids = path.split("/")[-1]

    return ids

def request(url):
    thing = req_get(url, headers=header)

    return thing

def __check_dir(directory):
    if not isdir(directory):
        makedirs(directory)

def var_excape(string):
    # Enhance character replacement for filenames
    replacements = {
        "\\": "",
        "/": "",
        ":": "",
        "*": "",
        "?": "",
        "\"": "",
        "<": "",
        ">": "",
        "|": "-",
        "&": "and",
        "$": "s",
        "'": "",
        "`": "",
    }
    
    for old, new in replacements.items():
        string = string.replace(old, new)
    
    # Remove any other non-printable characters
    string = ''.join(char for char in string if char.isprintable())
    
    return string.strip()

def convert_to_date(date: str):
    if date == "0000-00-00":
        date = "0001-01-01"

    elif date.isdigit():
        date = f"{date}-01-01"

    date = datetime.strptime(date, "%Y-%m-%d")

    return date

def what_kind(link):
    url = request(link).url

    if url.endswith("/"):
        url = url[:-1]

    return url

def __get_tronc(string):
    l_encoded = len(
        string.encode()
    )

    if l_encoded > 242:
        n_tronc = len(string) - l_encoded - 242
    else:
        n_tronc = 242

    return n_tronc

def __get_dir(song_metadata, output_dir, method_save):
    if song_metadata is None:
        raise ValueError("song_metadata cannot be None")

    if 'show' in song_metadata and 'name' in song_metadata:
        show = var_excape(song_metadata.get('show', ''))
        episode = var_excape(song_metadata.get('name', ''))
        if show and episode:
            dir_name = f"{show} - {episode}"
        elif show:
            dir_name = show
        elif episode:
            dir_name = episode
        else:
            dir_name = "Unknown Episode"
    else:
        album = var_excape(song_metadata.get('album', ''))
        artist = var_excape(song_metadata.get('artist', ''))
        if method_save == 0:
            dir_name = f"{album} - {artist}"
        elif method_save == 1:
            dir_name = f"{artist}"
        elif method_save == 2:
            dir_name = f"{album} - {artist}"
        elif method_save == 3:
            dir_name = f"{album} - {artist}"
        else:
            dir_name = "Unknown"

    final_dir = join(output_dir, dir_name)
    if not isdir(final_dir):
        makedirs(final_dir)

    return final_dir

def set_path(
    song_metadata, output_dir,
    song_quality, file_format, method_save,
    is_episode=False
):
    if song_metadata is None:
        raise ValueError("song_metadata cannot be None")

    if is_episode:
        show = var_excape(song_metadata.get('show', ''))
        episode = var_excape(song_metadata.get('name', ''))
        if show and episode:
            song_name = f"{show} - {episode}"
        elif show:
            song_name = show
        elif episode:
            song_name = episode
        else:
            song_name = "Unknown Episode"
    else:
        album = var_excape(song_metadata.get('album', ''))
        artist = var_excape(song_metadata.get('artist', ''))
        music = var_excape(song_metadata.get('music', ''))

        if method_save == 0:
            discnum = song_metadata.get('discnum', '')
            tracknum = song_metadata.get('tracknum', '')
            song_name = f"{album} CD {discnum} TRACK {tracknum}"

        elif method_save == 1:
            song_name = f"{music} - {artist}"

        elif method_save == 2:
            isrc = song_metadata.get('isrc', '')
            song_name = f"{music} - {artist} [{isrc}]"

        elif method_save == 3:
            discnum = song_metadata.get('discnum', '')
            tracknum = song_metadata.get('tracknum', '')
            song_name = f"{discnum}|{tracknum} - {music} - {artist}"

    # Ensure the song_name is not too long
    max_length = 255 - len(output_dir) - len(file_format) - len(f" ({song_quality})")
    song_name = song_name[:max_length]

    song_dir = __get_dir(song_metadata, output_dir, method_save)
    __check_dir(song_dir)
    n_tronc = __get_tronc(song_name)
    song_path = f"{song_dir}/{song_name[:n_tronc]} ({song_quality}){file_format}"

    return song_path

def create_zip(
    tracks: list[Track],
    output_dir=None,
    song_metadata=None,
    song_quality=None,
    method_save=0,
    zip_name=None
):
    if not zip_name:
        album = var_excape(song_metadata.get('album', ''))
        song_dir = __get_dir(song_metadata, output_dir, method_save)

        if method_save == 0:
            zip_name = f"{album}"

        elif method_save == 1:
            artist = var_excape(song_metadata.get('ar_album', ''))
            zip_name = f"{album} - {artist}"

        elif method_save == 2:
            artist = var_excape(song_metadata.get('ar_album', ''))
            upc = song_metadata.get('upc', '')
            zip_name = f"{album} - {artist} {upc}"

        elif method_save == 3:
            artist = var_excape(song_metadata.get('ar_album', ''))
            upc = song_metadata.get('upc', '')
            zip_name = f"{album} - {artist} {upc}"

        n_tronc = __get_tronc(zip_name)
        zip_name = zip_name[:n_tronc]
        zip_name += f" ({song_quality}).zip"
        zip_path = f"{song_dir}{zip_name}"
    else:
        zip_path = zip_name

    z = ZipFile(zip_path, "w", ZIP_DEFLATED)

    for track in tracks:
        if not track.success:
            continue

        c_song_path = track.song_path
        song_path = basename(c_song_path)

        if not isfile(c_song_path):
            continue

        z.write(c_song_path, song_path)

    z.close()

    return zip_path

def trasform_sync_lyric(lyric):
    sync_array = []

    for a in lyric:
        if "milliseconds" in a:
            arr = (
                a['line'], int(a['milliseconds'])
            )

            sync_array.append(arr)

    return sync_array