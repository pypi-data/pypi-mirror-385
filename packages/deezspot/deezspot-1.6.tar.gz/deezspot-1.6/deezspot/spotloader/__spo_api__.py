#!/usr/bin/python3

from deezspot.easy_spoty import Spo
from datetime import datetime
from deezspot.libutils.utils import convert_to_date
import traceback

def tracking(ids, album=None):
    datas = {}
    try:
        json_track = Spo.get_track(ids)

        if not album:
            album_ids = json_track['album']['id']
            json_album = Spo.get_album(album_ids)
            datas['image'] = json_album['images'][0]['url']
            datas['image2'] = json_album['images'][1]['url']
            datas['image3'] = json_album['images'][2]['url']
            datas['genre'] = " & ".join(json_album['genres'])

            ar_album = [
                artist['name']
                for artist in json_album['artists']
            ]

            datas['ar_album'] = " & ".join(ar_album)
            datas['album'] = json_album['name']
            datas['label'] = json_album['label']

            external_ids = json_album['external_ids']

            if external_ids:
                datas['upc'] = external_ids['upc']
            else:
                datas['upc'] = "Unknown"

            datas['nb_tracks'] = json_album['total_tracks']

        datas['music'] = json_track['name']

        artists = [
            artist['name']
            for artist in json_track['artists']
        ]

        datas['artist'] = " & ".join(artists)
        datas['tracknum'] = json_track['track_number']
        datas['discnum'] = json_track['disc_number']

        datas['year'] = convert_to_date(
            json_track['album']['release_date']
        )

        datas['bpm'] = "Unknown"
        datas['duration'] = json_track['duration_ms'] // 1000

        external_ids = json_track['external_ids']

        if external_ids:
            datas['isrc'] = external_ids['isrc']

        datas['gain'] = "Unknown"
        datas['ids'] = ids
    except Exception as e:
        traceback.print_exc()  # Print traceback
        # Optionally, handle or log the exception here
        return None

    return datas

def tracking_album(album_json):
    song_metadata = {}
    try:
        song_metadata = {
            "music": [],
            "artist": [],
            "tracknum": [],
            "discnum": [],
            "bpm": [],
            "duration": [],
            "isrc": [],
            "gain": [],
            "ids": [],
            "image": album_json['images'][0]['url'],
            "image2": album_json['images'][1]['url'],
            "image3": album_json['images'][2]['url'],
            "album": album_json['name'],
            "label": album_json['label'],
            "year": convert_to_date(album_json['release_date']),
            "nb_tracks": album_json['total_tracks'],
            "genre": " & ".join(album_json['genres'])
        }

        ar_album = [
            artist['name']
            for artist in album_json['artists']
        ]

        song_metadata['ar_album'] = " & ".join(ar_album)

        external_ids = album_json['external_ids']

        if external_ids:
            song_metadata['upc'] = external_ids['upc']
        else:
            song_metadata['upc'] = "Unknown"

        sm_items = song_metadata.items()

        for track in album_json['tracks']['items']:
            c_ids = track['id']
            detas = tracking(c_ids, album=True)

            for key, item in sm_items:
                if type(item) is list:
                    song_metadata[key].append(detas[key])
    except Exception as e:
        traceback.print_exc()  # Print traceback
        # Optionally, handle or log the exception here
        return None

    return song_metadata

def tracking_episode(ids):
    datas = {}
    try:
        json_episode = Spo.get_episode(ids)

        datas['audio_preview_url'] = json_episode.get('audio_preview_url', '')
        datas['description'] = json_episode.get('description', '')
        datas['duration'] = json_episode.get('duration_ms', 0) // 1000
        datas['explicit'] = json_episode.get('explicit', False)
        datas['external_urls'] = json_episode.get('external_urls', {}).get('spotify', '')
        datas['href'] = json_episode.get('href', '')
        datas['html_description'] = json_episode.get('html_description', '')
        datas['id'] = json_episode.get('id', '')
        datas['image'] = json_episode['images'][0]['url'] if json_episode.get('images') else ''
        datas['image2'] = json_episode['images'][1]['url'] if len(json_episode.get('images', [])) > 1 else ''
        datas['image3'] = json_episode['images'][2]['url'] if len(json_episode.get('images', [])) > 2 else ''
        datas['is_externally_hosted'] = json_episode.get('is_externally_hosted', False)
        datas['is_playable'] = json_episode.get('is_playable', False)
        datas['language'] = json_episode.get('language', '')
        datas['languages'] = " & ".join(json_episode.get('languages', []))
        datas['name'] = json_episode.get('name', '')
        datas['release_date'] = convert_to_date(json_episode.get('release_date', ''))
        datas['show'] = json_episode.get('show', {}).get('name', '')
        datas['publisher'] = json_episode.get('show', {}).get('publisher', '')
        datas['ids'] = ids
    except Exception as e:
        traceback.print_exc() 
        return None

    return datas