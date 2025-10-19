from dataclasses import dataclass
from typing import Callable, Optional
import numpy as np

from wsignals import Signal


@dataclass
class StreamOptions:
	duration: float
	rate: Optional[int] = None
	channels: Optional[int] = None

	def __iter__(self):
		return iter((self.duration, self.rate, self.channels))

@dataclass
class StreamData:
	audio: Optional['Audio'] = None
	last: bool = False

	def __iter__(self):
		return iter((self.audio, self.last))

# audio (None: zero audio), is_last (eof)
StreamAudio = tuple[Optional['Audio'], bool]
# duration
AudioReaderType = Callable[[StreamOptions], StreamData]
# frame
AudioWriterType = Callable[[StreamData], None]


class UnsupportedAudioForm(Exception):
	'''Unsupported audio form (rate or channels)'''


class Audio:
	data: np.ndarray
	rate: int

	samples: int
	channels: int
	duration: float

	def __init__(self, data: np.ndarray, rate: int):
		data.flags.writeable = False  # make array immutable to ensure Audio immutability
		self.data = data
		self.rate = rate

		# extract sample count and channel count from array shape (size of dimensions)
		samples, self.channels = data.shape
		self.samples = samples
		self.duration = samples / rate

	def stream(self) -> 'AudioReader':
		return AudioReader(self)
	
	def assert_form(self, rate: int, channels: int):
		if self.rate != rate or self.channels != channels:
			raise UnsupportedAudioForm()
	
	def formed(self, rate: Optional[int] = None, channels: Optional[int] = None) -> 'Audio':
		fsamples = self.samples
		frate = self.rate
		fchannels = self.channels
		data = self.data

		# data = self.data.copy()
		# removed as unnecessary (needs testing)

		if not rate: rate = frate
		if not channels: channels = fchannels

		# If required channels does not satisfy current channels
		# merge current channels in one and expand to required
		if fchannels != channels:
			data = data.mean(axis=1, keepdims=True)
			data = np.tile(data, (1, channels))

		# If required rate does not satisfy current rate
		# perform linear interpolation by rate ratio among current data
		if frate != rate and fsamples != 0:
			ratio = frate / rate
			x = np.arange(0, fsamples, ratio)
			xp = np.arange(0, fsamples)
			t = data.transpose()  # swap array dimensions
			data = np.zeros((len(x), channels))  # allocate new array to store data in
			# apply interpolation to each channel separately
			for i, c in enumerate(t):
				data[:, i] = np.interp(x, xp, c)
		
		return Audio(
			data=data,
			rate=rate
		)
	
	def __getitem__(self, i: slice) -> 'Audio':
		if i.step is not None: raise ValueError('Step is not supported')
		rate = self.rate
		start = int((i.start or 0) * rate)
		stop = int((i.stop or self.duration) * rate)
		return Audio(
			data=self.data[start:stop],
			rate=rate
		)


class AudioReader:
	audio: Audio
	position: float
	volume: float
	pitch: float
	end: Signal
	_end_handled: bool = False
	closed: bool = False

	def __init__(self, audio: Audio, volume: float = 1.0, pitch: float = 1.0, position: float = 0.0):
		self.audio = audio

		self.end = Signal()

		self.volume = volume
		self.pitch = pitch
		self.position = position
	
	def __call__(self, options: StreamOptions) -> StreamAudio:
		if self.closed: return StreamData(None, True)

		duration = options.duration
		pos = self.position
		pitch = self.pitch
		full_audio = self.audio
		full_duration = self.duration

		if pos == full_duration: return StreamData(None, True)

		if pitch == 0.0: return StreamData(None, False)

		end = min(pos + (duration * pitch), full_duration)
		self.position = end

		audio_fragment = full_audio[pos:end]
		data = audio_fragment.data

		volume = self.volume
		if volume != 1.0: data = data * volume
		# print(pitch, full_audio.rate)
		last = end==full_duration
		if last: self.end.call()

		return StreamData(
			audio=Audio(data, int(pitch * full_audio.rate)),
			last=last
		)
	
	def close(self):
		self.closed = True

	@property
	def samples(self) -> int:
		return self.audio.samples
	
	@property
	def rate(self) -> int:
		return self.audio.rate

	@property
	def channels(self) -> int:
		return self.audio.channels
	
	@property
	def duration(self) -> int:
		return self.audio.duration

