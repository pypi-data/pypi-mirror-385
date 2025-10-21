from .opcodes import Opcodes
from .message import *


OpcodesToMessages = {
    Opcodes.play: Play,
    Opcodes.pause: Pause,
    Opcodes.resume: Resume,
    Opcodes.stop: Stop,
    Opcodes.seek: Seek,
    Opcodes.playback_update: PlaybackUpdate,
    Opcodes.volume_update: VolumeUpdate,
    Opcodes.set_volume: SetVolume,
    Opcodes.set_speed: SetSpeed,
	Opcodes.version: Version,
    Opcodes.ping: Ping,
    Opcodes.pong: Pong,
	Opcodes.initial: Initial,
    Opcodes.play_update: PlayUpdate,
    Opcodes.set_playlist_item: SetPlaylistItem
}

MessagesToOpcodes = {v:k for k,v in OpcodesToMessages.items()}