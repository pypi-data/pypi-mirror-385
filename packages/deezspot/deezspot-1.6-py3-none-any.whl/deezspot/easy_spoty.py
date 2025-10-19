from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException
from deezspot.exceptions import InvalidLink

class Spo:
    __error_codes = [404, 400]

    @classmethod
    def __init__(cls, client_id=None, client_secret=None):
        if not client_id or not client_secret:
            raise SpotifyException(http_status=400, code=400, msg="No client_id or client_secret provided. Pass them as arguments or set them as environment variables.")

        auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        cls.__api = Spotify(auth_manager=auth_manager)

    @classmethod
    def __lazy(cls, results):
        albums = results['items']

        while results['next']:
            results = cls.__api.next(results)
            albums.extend(results['items'])

        return results

    @classmethod
    def get_track(cls, ids):
        try:
            track_json = cls.__api.track(ids)
        except SpotifyException as error:
            if error.http_status in cls.__error_codes:
                raise InvalidLink(ids)

        return track_json

    @classmethod
    def get_album(cls, ids):
        try:
            album_json = cls.__api.album(ids)
        except SpotifyException as error:
            if error.http_status in cls.__error_codes:
                raise InvalidLink(ids)

        tracks = album_json['tracks']
        cls.__lazy(tracks)

        return album_json

    @classmethod
    def get_playlist(cls, ids):
        try:
            playlist_json = cls.__api.playlist(ids)
        except SpotifyException as error:
            if error.http_status in cls.__error_codes:
                raise InvalidLink(ids)

        tracks = playlist_json['tracks']
        cls.__lazy(tracks)

        return playlist_json

    @classmethod
    def get_episode(cls, ids):
        try:
            episode_json = cls.__api.episode(ids)
        except SpotifyException as error:
            if error.http_status in cls.__error_codes:
                raise InvalidLink(ids)

        return episode_json

    @classmethod
    def search(cls, query):
        search = cls.__api.search(query)

        return search