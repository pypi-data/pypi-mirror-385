import numpy as np

from wauxio import Audio, AudioWriterType, StreamData, StreamOptions


class AudioStack:
	buffer: np.ndarray
	rate: int
	channels: int
	samples: int
	position: int = 0
	last: bool = False
	
	def __init__(self, rate: int, channels: int, samples: int):
		self.rate = rate
		self.channels = channels
		self.samples = samples
		self.buffer = np.zeros((samples, channels), np.float32)
	
	def push(self, audio: StreamData):
		audio, last = audio
		self.last = last
		if not audio: return
		data = audio.formed(self.rate, self.channels).data
		req = len(data)
		buf = self.buffer
		cap = len(buf)
		if req >= cap:
			self.position = cap
			buf[:] = data[-cap:]
			return
		
		pos = self.position
		free = cap - pos
		if free >= req:
			self.position = pos + req
			buf[pos:pos+req] = data
			return
		
		moved = req - free
		buf[:-req] = buf[moved:pos]
		pos -= moved

		self.position = cap
		buf[pos:] = data

	def pull(self, options: StreamOptions) -> StreamData:
		duration = options.duration
		rate = self.rate
		pos = self.position
		size = int(duration * rate)
		end = min(size, pos)
		buf = self.buffer
		data = buf[:end].copy()

		# move
		buf[:pos-end] = buf[end:pos]
		self.position = pos - end

		# if len(data) < size:
		# 	rec = size - len(data)
		# 	data = np.concatenate([data, np.zeros((rec, buf.shape[1]), dtype=np.float32)])

		return StreamData(
			Audio(data, rate),
			self.last and end == pos
		)


class AudioDrain:
	buffer: np.ndarray
	rate: int
	position: int = 0
	output: AudioWriterType

	channels: int
	samples: int
	
	def __init__(self, rate: int, channels: int, samples: int, output: AudioWriterType):
		self.rate = rate
		self.channels = channels
		self.samples = samples
		self.buffer = np.zeros((samples, channels), np.float32)
		self.output = output
	
	def push(self, audio: StreamData) -> None:
		audio, last = audio
		if not audio:
			if last: output(StreamData(None, True))
			return
		data = audio.formed(self.rate, self.channels).data
		buf = self.buffer
		rate = self.rate
		samples = self.samples
		channels = self.channels
		pos = self.position
		
		ccat = np.concatenate((buf[:pos], data))
		clen = len(ccat)
		output = self.output
		i = 0
		while clen - i >= samples:
			output(StreamData(
				Audio(ccat[i:i+samples], rate),
				False
			))
			i += samples
		
		if last: output(StreamData(None, True))
		
		buf[:] = np.concatenate(( ccat[i:], np.zeros(( samples - (clen - i), channels )) ))
		self.position = clen - i
