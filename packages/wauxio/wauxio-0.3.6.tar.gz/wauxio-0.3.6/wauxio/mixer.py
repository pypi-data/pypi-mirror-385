from typing import Callable, Optional
import numpy as np
from threading import Lock

from wauxio import Audio, AudioReaderType, StreamData, StreamOptions


class AudioMixer:
	inputs: list[AudioReaderType]
	lock: Lock = Lock()
	rate: int = 48000
	channels: int = 2

	def __init__(self, rate: int = 48000, channels: int = 2):
		self.rate = rate
		self.channels = channels
		self.inputs = list()
	
	def add(self, inp: AudioReaderType):
		self.inputs.append(inp)
	
	def mix(self, options: StreamOptions) -> StreamData:
		duration = options.duration
		rate = options.rate or self.rate
		channels = options.channels or self.channels

		samples = int(rate * duration)

		fdata: np.ndarray = np.zeros((samples, channels), dtype=np.float32)

		with self.lock:
			inputs = self.inputs
			for i in range(len(inputs)-1, -1, -1):
				audio, last = inputs[i](
					StreamOptions(duration, rate, channels)
				)
				# Mix audio if it's not zero audio (None)
				if audio is not None:
					data = audio.formed(rate, channels).data
					size = len(data)
					if size == samples: fdata += data
					elif size > samples: fdata += data[:samples]
					else: fdata[:size] += data
				# Remove input if this is last audio
				if last: del inputs[i]
		
		fdata = np.clip(fdata, -1.0, 1.0)
		return StreamData(
			Audio(fdata, rate),
			False
		)
	
	__call__ = mix

