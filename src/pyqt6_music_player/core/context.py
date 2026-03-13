from dataclasses import dataclass

from pyqt6_music_player.audio import AudioPlayerService
from pyqt6_music_player.models import Playlist, VolumeModel
from pyqt6_music_player.services import PlaybackService, PlaylistService
from pyqt6_music_player.view_models import (
    PlaybackViewModel,
    PlaylistViewModel,
    VolumeViewModel,
)


@dataclass
class AppContext:
    """Holds all application-level dependencies."""

    # -- Audio --
    audio_player: AudioPlayerService

    # -- Models --
    playlist_model: Playlist
    volume_model: VolumeModel

    # -- Services --
    playlist_service: PlaylistService
    playback_service: PlaybackService

    # -- ViewModels --
    playback_viewmodel: PlaybackViewModel
    playlist_viewmodel: PlaylistViewModel
    volume_viewmodel: VolumeViewModel


def build_context():
    """Construct and wire all application dependencies."""
    # -- Audio --
    audio_player = AudioPlayerService()

    # -- Models --
    playlist_model = Playlist()
    volume_model = VolumeModel()

    # -- Services --
    playlist_service = PlaylistService(playlist_model)
    playback_service = PlaybackService(audio_player, playlist_service)

    # -- ViewModels --
    playback_viewmodel = PlaybackViewModel(playlist_service, playback_service)
    playlist_viewmodel = PlaylistViewModel(playlist_service)
    volume_viewmodel = VolumeViewModel(volume_model)

    return AppContext(
        playlist_model=playlist_model,
        volume_model=volume_model,
        playlist_service=playlist_service,
        playback_service=playback_service,
        audio_player=audio_player,
        playback_viewmodel=playback_viewmodel,
        playlist_viewmodel=playlist_viewmodel,
        volume_viewmodel=volume_viewmodel,
    )
