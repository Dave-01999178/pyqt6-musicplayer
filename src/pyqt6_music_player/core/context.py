from dataclasses import dataclass

from pyqt6_music_player.audio import AudioPlayerService
from pyqt6_music_player.models import PlaybackState, Playlist, VolumeModel
from pyqt6_music_player.services import PlaybackService, PlaylistService
from pyqt6_music_player.view_models import (
    PlaybackViewModel,
    PlaylistViewModel,
    VolumeViewModel,
)


@dataclass
class AppContext:
    # --- Player engine ---
    audio_player: AudioPlayerService

    # --- State/Models ---
    playback_state: PlaybackState
    playlist_model: Playlist
    volume_model: VolumeModel

    # --- Service ---
    playback_service: PlaybackService

    # --- ViewModels ---
    playback_viewmodel: PlaybackViewModel
    playlist_viewmodel: PlaylistViewModel
    volume_viewmodel: VolumeViewModel


def build_context():
    # --- Player engine ---
    audio_player = AudioPlayerService()

    # --- Models ---
    playback_state = PlaybackState()
    playlist_model = Playlist()
    volume_model = VolumeModel()

    # -- Service ---
    playlist_service = PlaylistService(playlist_model)
    playback_service = PlaybackService(audio_player, playback_state, playlist_service)

    # --- Viewmodels ---
    playback_viewmodel = PlaybackViewModel(playlist_service, playback_service)
    playlist_viewmodel = PlaylistViewModel(playlist_service)
    volume_viewmodel = VolumeViewModel(volume_model, audio_player)

    return AppContext(
        audio_player=audio_player,
        playback_state=playback_state,
        playlist_model=playlist_model,
        volume_model=volume_model,
        playback_service=playback_service,
        playback_viewmodel=playback_viewmodel,
        playlist_viewmodel=playlist_viewmodel,
        volume_viewmodel=volume_viewmodel
    )
