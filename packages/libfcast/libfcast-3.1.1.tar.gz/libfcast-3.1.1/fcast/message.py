from dataclasses import dataclass
import struct
from enum import Enum
from typing import Optional
import json

import logging

l = logging.getLogger(__name__)


@dataclass
class MetadataType:
	title: str = None
	thumbnailUrl: str = None
	custom = None

class PlaybackState(Enum):
	idle: int = 0
	playing: int = 1
	paused: int = 2


@dataclass
class Message:

	@property
	def opcode(self):
		from .utils import MessagesToOpcodes
		l.debug(f"{type(self)} opcode: {MessagesToOpcodes[type(self)]}")
		return MessagesToOpcodes[type(self)]

	@property
	def header(self):
		size = 1
		if self.body: size += self.size
		if size > 32000: raise ValueError("Message size is bigger than 32000")
		return struct.pack("<I", size) + struct.pack("B", self.opcode)
	
	@property
	def as_bytes(self) -> bytes:
		data = self.header
		if self.body: data += self.body
		return data
	
	def serialize(self):
		...

	@property
	def size(self):
		return len(self.serialize())
	
	@property
	def body(self):
		return self.serialize()
	

@dataclass
class Play(Message):
	container: str #The MIME type (video/mp4)
	url: Optional[str] = None #The URL to load (optional)
	content: Optional[str] = None #The content to load (i.e. a DASH manifest, optional)
	time: float = 0 #The time to start playing in seconds
	volume: float = None # The desired volume (0-1)
	speed: float = 1.0 #The factor to multiply playback speed by (defaults to 1.0)
	headers: Optional[dict] = None #HTTP request headers to add to the play request Map<string, string>
	metadata: MetadataType = None

	def serialize(self):
		res = {
			"container": self.container,
			"time": self.time,
			"speed": self.speed
		}
		if u:=self.url: res["url"] = u
		if c:=self.content: res["content"] = c
		if h:=self.headers: res["headers"] = h
		if m:=self.metadata: res["metadata"] = m.__dict__

		return json.dumps(res).encode(encoding="utf-8")


@dataclass
class Seek(Message):
	time: float = 0 #The time to seek to in seconds

	def serialize(self):
		return json.dumps({"time": self.time}).encode(encoding="utf-8")


@dataclass
class PlaybackUpdate(Message):
	generationTime: float #The time the packet was generated (unix time milliseconds)
	state: PlaybackState # The playback state
	time: int = None # The current time playing in seconds
	duration: int = None # The duration in seconds
	speed: float = None # The playback speed factor
	itemIndex: int = None # The playlist item index currently being played on receiver

	def serialize(self):
		res = {
			"generationTime": self.generationTime,
			"state": self.state.value,
		}
		if t:=self.time: res["time"] = t
		if d:=self.duration: res["duration"] = d
		if s:=self.speed: res["speed"] = s
		if i:=self.itemIndex: res["itemIndex"] = i

		return json.dumps(res).encode(encoding="utf-8")


@dataclass
class VolumeUpdate(Message):
	generation_time: float #The time the packet was generated (unix time milliseconds)
	volume: float # The current volume (0-1)

	def serialize(self):
		res = {
			"generationTime": self.generation_time,
			"volume": self.volume
		}
		return json.dumps(res).encode(encoding="utf-8")


@dataclass
class SetVolume(Message):
	volume: float = 0 # The desired volume (0-1)

	def serialize(self):
		return json.dumps({"volume": self.volume}).encode(encoding="utf-8")


@dataclass
class PlaybackError(Message):
	message: str

	def serialize(self):
		return json.dumps({"message": self.message}).encode(encoding="utf-8")


@dataclass
class SetSpeed(Message):
	speed: float = 0 # The factor to multiply playback speed by.

	def serialize(self):
		return json.dumps({"volume": self.speed}).encode(encoding="utf-8")


@dataclass
class Version(Message):
	version: int = 3 # Protocol version number (integer)

	def serialize(self):
		return json.dumps({"version": self.version}).encode(encoding="utf-8")	


@dataclass
class Initial(Message):
	displayName: str = None
	appName: str = None
	appVersion: str = None
	playData: Play = None

	def serialize(self):
		res = {
			"displayName": self.displayName,
			"appName": self.appName,
			"appVersion": self.appVersion,
		}
		if pd:=self.playData:
			if t:=type(pd) == Play:
				res["playData"]: json.loads(self.playData.serialize().decode())
			elif t == dict:
				res["playData"] = pd

		return json.dumps(res).encode(encoding="utf-8")


@dataclass
class PlayUpdate(Message):
	generationTime: float #The time the packet was generated (unix time milliseconds)
	playData: Play = None

	def serialize(self):
		res = {
			"generationTime": self.generationTime,
			"playData": json.loads(self.playData.serialize().decode())
		}
		return json.dumps(res).encode(encoding="utf-8")
	

@dataclass
class SetPlaylistItem(Message):
	itemIndex: int # The playlist item index to play on receiver

	def serialize(self):
		return json.dumps({"itemIndex": self.itemIndex}).encode(encoding="utf-8")


@dataclass
class Pause(Message):
	...

@dataclass
class Stop(Message):
	...

@dataclass
class Resume(Message):
	...

@dataclass
class Ping(Message):
	...

@dataclass
class Pong(Message):
	...
