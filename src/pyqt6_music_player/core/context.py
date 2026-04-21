from dataclasses import dataclass

from pyqt6_music_player.audio import AudioPlayerService
from pyqt6_music_player.models import Playlist, Volume
from pyqt6_music_player.services import PlaybackService, PlaylistService, PlaybackOrder, TrackNavigator
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
    volume_model: Volume

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
    volume_model = Volume()

    # -- Services --
    playback_order = PlaybackOrder()
    track_navigator = TrackNavigator(playback_order)

    playlist_service = PlaylistService(playlist_model, playback_order)
    playback_service = PlaybackService(
        audio_player,
        playlist_service,
        track_navigator,
    )

    # -- ViewModels --
    playback_viewmodel = PlaybackViewModel(playback_service)
    playlist_viewmodel = PlaylistViewModel(playlist_service)
    volume_viewmodel = VolumeViewModel(volume_model)

    # -- Wiring --
    playlist_service.initial_tracks_added.connect(playback_viewmodel.enable_controls)
    volume_model.volume_changed.connect(playback_service.set_volume)

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
