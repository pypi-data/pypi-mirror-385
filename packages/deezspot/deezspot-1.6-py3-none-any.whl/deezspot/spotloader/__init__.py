#!/usr/bin/python3
import traceback
from os.path import isfile
from deezspot.easy_spoty import Spo
from librespot.core import Session
from deezspot.exceptions import InvalidLink
from deezspot.spotloader.__spo_api__ import tracking, tracking_album, tracking_episode
from deezspot.spotloader.spotify_settings import stock_quality
from deezspot.libutils.utils import (
    get_ids,
    link_is_valid,
    what_kind,
)
from deezspot.models import (
    Track,
    Album,
    Playlist,
    Preferences,
    Smart,
    Episode
)
from deezspot.spotloader.__download__ import (
    DW_TRACK,
    DW_ALBUM,
    DW_PLAYLIST,
    DW_EPISODE,
    Download_JOB,
)
from deezspot.libutils.others_settings import (
    stock_output,
    stock_recursive_quality,
    stock_recursive_download,
    stock_not_interface,
    stock_zip,
    method_save,
    is_thread,
)
class SpoLogin:
    def __init__(self, credentials_path: str, client_id: str, client_secret: str) -> None:
        self.credentials_path = credentials_path
        self.client_id = client_id
        self.client_secret = client_secret
        self.__initialize_session()

        # Initialize Spo with credentials
        Spo(client_id=self.client_id, client_secret=self.client_secret)

    def __initialize_session(self) -> None:
        session_builder = Session.Builder()
        session_builder.conf.stored_credentials_file = self.credentials_path

        if isfile(self.credentials_path):
            session = session_builder.stored_file().create()
        else:
            raise FileNotFoundError("Please fill your credentials.json location!")

        Download_JOB(session)

    def download_track(
        self, link_track,
        output_dir=stock_output,
        quality_download=stock_quality,
        recursive_quality=stock_recursive_quality,
        recursive_download=stock_recursive_download,
        not_interface=stock_not_interface,
        method_save=method_save,
        is_thread=is_thread
    ) -> Track:
        try:
            link_is_valid(link_track)
            ids = get_ids(link_track)
            song_metadata = tracking(ids)

            preferences = Preferences()

            preferences.link = link_track
            preferences.song_metadata = song_metadata
            preferences.quality_download = quality_download
            preferences.output_dir = output_dir
            preferences.ids = ids
            preferences.recursive_quality = recursive_quality
            preferences.recursive_download = recursive_download
            preferences.not_interface = not_interface
            preferences.method_save = method_save
            preferences.is_episode = False

            if not is_thread:
                track = DW_TRACK(preferences).dw()
            else:
                track = DW_TRACK(preferences).dw2()

            return track
        except Exception as e:
            traceback.print_exc()
            raise e

    def download_album(
        self, link_album,
        output_dir=stock_output,
        quality_download=stock_quality,
        recursive_quality=stock_recursive_quality,
        recursive_download=stock_recursive_download,
        not_interface=stock_not_interface,
        make_zip=stock_zip,
        method_save=method_save,
        is_thread=is_thread
    ) -> Album:
        try:
            link_is_valid(link_album)
            ids = get_ids(link_album)
            album_json = Spo.get_album(ids)
            song_metadata = tracking_album(album_json)

            preferences = Preferences()

            preferences.link = link_album
            preferences.song_metadata = song_metadata
            preferences.quality_download = quality_download
            preferences.output_dir = output_dir
            preferences.ids = ids
            preferences.json_data = album_json
            preferences.recursive_quality = recursive_quality
            preferences.recursive_download = recursive_download
            preferences.not_interface = not_interface
            preferences.method_save = method_save
            preferences.make_zip = make_zip
            preferences.is_episode = False

            if not is_thread:
                album = DW_ALBUM(preferences).dw()
            else:
                album = DW_ALBUM(preferences).dw2()

            return album
        except Exception as e:
            traceback.print_exc()
            raise e

    def download_playlist(
        self, link_playlist,
        output_dir=stock_output,
        quality_download=stock_quality,
        recursive_quality=stock_recursive_quality,
        recursive_download=stock_recursive_download,
        not_interface=stock_not_interface,
        make_zip=stock_zip,
        method_save=method_save,
        is_thread=is_thread
    ) -> Playlist:
        try:
            link_is_valid(link_playlist)
            ids = get_ids(link_playlist)

            song_metadata = []
            playlist_json = Spo.get_playlist(ids)

            for track in playlist_json['tracks']['items']:
                is_track = track['track']

                if not is_track:
                    continue

                external_urls = is_track['external_urls']

                if not external_urls:
                    c_song_metadata = f"The track \"{is_track['name']}\" is not available on Spotify :("
                else:
                    ids = get_ids(external_urls['spotify'])
                    c_song_metadata = tracking(ids)

                song_metadata.append(c_song_metadata)

            preferences = Preferences()

            preferences.link = link_playlist
            preferences.song_metadata = song_metadata
            preferences.quality_download = quality_download
            preferences.output_dir = output_dir
            preferences.ids = ids
            preferences.json_data = playlist_json
            preferences.recursive_quality = recursive_quality
            preferences.recursive_download = recursive_download
            preferences.not_interface = not_interface
            preferences.method_save = method_save
            preferences.make_zip = make_zip
            preferences.is_episode = False

            if not is_thread:
                playlist = DW_PLAYLIST(preferences).dw()
            else:
                playlist = DW_PLAYLIST(preferences).dw2()

            return playlist
        except Exception as e:
            traceback.print_exc()
            raise e
    
    def download_episode(
        self, link_episode,
        output_dir=stock_output,
        quality_download=stock_quality,
        recursive_quality=stock_recursive_quality,
        recursive_download=stock_recursive_download,
        not_interface=stock_not_interface,
        method_save=method_save,
        is_thread=is_thread,
    ) -> Episode:
        try:
            link_is_valid(link_episode)
            ids = get_ids(link_episode)
            episode_json = Spo.get_episode(ids)
            episode_metadata = tracking_episode(ids)

            preferences = Preferences()

            preferences.link = link_episode
            preferences.song_metadata = episode_metadata
            preferences.output_dir = output_dir
            preferences.ids = ids
            preferences.json_data = episode_json
            preferences.recursive_quality = recursive_quality
            preferences.recursive_download = recursive_download
            preferences.not_interface = not_interface
            preferences.method_save = method_save
            preferences.is_episode = True

            if not is_thread:
                episode = DW_EPISODE(preferences).dw()
            else:
                episode = DW_EPISODE(preferences).dw2()

            return episode
        except Exception as e:
            traceback.print_exc()
            raise e

    def download_smart(
        self, link,
        output_dir=stock_output,
        quality_download=stock_quality,
        recursive_quality=stock_recursive_quality,
        recursive_download=stock_recursive_download,
        not_interface=stock_not_interface,
        make_zip=stock_zip,
        method_save=method_save
    ) -> Smart:
        try:
            link_is_valid(link)
            link = what_kind(link)
            smart = Smart()

            if "spotify.com" in link:
                source = "https://spotify.com"

            smart.source = source

            if "track/" in link:
                if not "spotify.com" in link:
                    raise InvalidLink(link)

                track = self.download_track(
                    link,
                    output_dir=output_dir,
                    quality_download=quality_download,
                    recursive_quality=recursive_quality,
                    recursive_download=recursive_download,
                    not_interface=not_interface,
                    method_save=method_save
                )

                smart.type = "track"
                smart.track = track

            elif "album/" in link:
                if not "spotify.com" in link:
                    raise InvalidLink(link)

                album = self.download_album(
                    link,
                    output_dir=output_dir,
                    quality_download=quality_download,
                    recursive_quality=recursive_quality,
                    recursive_download=recursive_download,
                    not_interface=not_interface,
                    make_zip=make_zip,
                    method_save=method_save
                )

                smart.type = "album"
                smart.album = album

            elif "playlist/" in link:
                if not "spotify.com" in link:
                    raise InvalidLink(link)

                playlist = self.download_playlist(
                    link,
                    output_dir=output_dir,
                    quality_download=quality_download,
                    recursive_quality=recursive_quality,
                    recursive_download=recursive_download,
                    not_interface=not_interface,
                    make_zip=make_zip,
                    method_save=method_save
                )

                smart.type = "playlist"
                smart.playlist = playlist

            elif "episode/" in link:
                if not "spotify.com" in link:
                    raise InvalidLink(link)

                episode = self.download_episode(
                    link,
                    output_dir=output_dir,
                    quality_download=quality_download,
                    recursive_quality=recursive_quality,
                    recursive_download=recursive_download,
                    not_interface=not_interface,
                    method_save=method_save
                )

                smart.type = "episode"
                smart.episode = episode

            return smart
        except Exception as e:
            traceback.print_exc()
            raise e