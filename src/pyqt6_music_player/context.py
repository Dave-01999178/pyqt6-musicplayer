from dataclasses import dataclass

from pyqt6_music_player.models import AudioPlayerService, PlaylistModel, VolumeModel
from pyqt6_music_player.view_models import (
    PlaybackControlViewModel,
    PlaylistViewModel,
    VolumeViewModel
)


@dataclass
class AppContext:
    # --- Player engine ---
    player_engine: AudioPlayerService

    # --- Models ---
    playlist_model: PlaylistModel
    volume_model: VolumeModel

    # --- ViewModels ---
    playback_viewmodel: PlaybackControlViewModel
    playlist_viewmodel: PlaylistViewModel
    volume_viewmodel: VolumeViewModel


def build_context():
    # --- Player engine ---
    player_engine = AudioPlayerService()

    # --- Models ---
    playlist_model = PlaylistModel()
    volume_model = VolumeModel()

    # --- ViewModels ---
    playback_viewmodel = PlaybackControlViewModel(playlist_model, player_engine)
    playlist_viewmodel = PlaylistViewModel(playlist_model)
    volume_viewmodel = VolumeViewModel(volume_model, player_engine)

    return AppContext(
        player_engine=player_engine,
        playlist_model=playlist_model,
        volume_model=volume_model,
        playback_viewmodel=playback_viewmodel,
        playlist_viewmodel=playlist_viewmodel,
        volume_viewmodel=volume_viewmodel
    )
