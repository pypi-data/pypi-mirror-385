from wauxio import AudioReaderType, AudioWriterType, StreamData, StreamOptions


class AudioOutput:
	delay: float = 0
	outputs: list[AudioWriterType]
	inp: AudioReaderType

	channels: int
	rate: int

	def __init__(
			self, 
			channels: int = 2, 
			rate: int = 48000
		):
		self.channels = channels
		self.rate = rate
		self.outputs = list()
	
	def listen(self, output: AudioWriterType):
		self.outputs.append(output)
	
	def connect(self, inp: AudioReaderType):
		self.inp = inp
	
	def tick(self, duration: float) -> StreamData:
		audio = self.inp(StreamOptions(
			duration, self.rate, self.channels
		)) if self.inp else StreamData(None, False)

		for out in self.outputs:
			out(audio)
		return audio
	
	async def run(self, delay: float = 0.5):
		import time
		import asyncio
		last = time.time()
		while True:
			await asyncio.sleep(delay)
			current = time.time()
			dt = current - last
			last = current
			self.tick(dt)
	
	def run_sync(self, delay: float = 0.5):
		import time
		last = time.time()
		while True:
			time.sleep(delay)
			current = time.time()
			dt = current - last
			last = current
			self.tick(dt)
