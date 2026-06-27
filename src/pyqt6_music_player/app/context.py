from dataclasses import dataclass

from pyqt6_music_player.audio import AudioPlayerService
from pyqt6_music_player.features import (
    PlaybackNavigator,
    PlaybackOrder,
    PlaybackService,
    PlaybackViewModel,
    Playlist,
    PlaylistService,
    PlaylistViewModel,
    Volume,
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


def build_context() -> AppContext:
    """Construct and wire all application dependencies."""
    # -- Models --
    playlist_model = Playlist()
    volume_model = Volume()

    # -- Shared ordering state (internal to playback subsystem) --
    playback_order = PlaybackOrder()
    track_navigator = PlaybackNavigator(playback_order)

    # -- Services --
    audio_player = AudioPlayerService()
    playlist_service = PlaylistService(playlist_model, playback_order)
    playback_service = PlaybackService(audio_player, playlist_service, track_navigator)

    # -- ViewModels --
    playback_viewmodel = PlaybackViewModel(playback_service)
    playlist_viewmodel = PlaylistViewModel(playlist_service)
    volume_viewmodel = VolumeViewModel(volume_model)

    # -- Wiring --
    playback_service.playback_started.connect(playlist_viewmodel.sync_active_row)
    playlist_service.initial_tracks_added.connect(playback_viewmodel.enable_controls)
    volume_model.volume_changed.connect(playback_service.set_volume)

    # Set initial volume
    audio_player.set_volume(volume_model.current_volume)

    return AppContext(
        audio_player=audio_player,
        playlist_model=playlist_model,
        volume_model=volume_model,
        playlist_service=playlist_service,
        playback_service=playback_service,
        playback_viewmodel=playback_viewmodel,
        playlist_viewmodel=playlist_viewmodel,
        volume_viewmodel=volume_viewmodel,
    )
