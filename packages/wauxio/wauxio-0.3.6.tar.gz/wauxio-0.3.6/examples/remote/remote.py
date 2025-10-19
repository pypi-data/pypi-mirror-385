import asyncio
from asyncio import Future
import os
from pathlib import Path
from typing import Optional
import json
import time

import numpy as np
import sounddevice as sd
import wave
import websockets

from wauxio import Audio
from wauxio.mixer import FlexMixer, MixerOutput
from wauxio.flex import FrameFlex
from wauxio.storage import FileSoundStorage
from wauxio.utils import AudioDrain, AudioStack
from wauxio.codecs.wave import from_wav



# SOUND STORAGE
def wave_codec(path):
	with wave.open(str(path), 'rb') as wf:
		return from_wav(wf)

# Memory cached sound storage, mounted for sounds directory
store = FileSoundStorage(Path('data/sounds/'))
store.use_sync_codec('.wav', wave_codec) # registers codec for .wav extension
store.mount_sync() # sync refresh whole sounds directory
print('File Sound Storage:', store.sounds)


RATE = 48000
CHANNELS = 1

# MIXER
mixer = FlexMixer(
	channels=CHANNELS,
	rate=RATE,
	max_frame_duration=5.0,
	min_frame_duration=0.05
)


# DEVICE OUTPUT
out_volume = 1.0
out_blocksize = 4410
out_stack: AudioStack = AudioStack(RATE, CHANNELS, out_blocksize*5)
mixer.listen(lambda f: out_stack.push(f.data))

def ocallback(outdata, frames, time, status):
	global out_volume
	f = out_stack.pull(frames/RATE)
	data = f.data.copy() * out_volume
	if len(data) < frames:
		rec = frames - len(data)
		data = np.concatenate((data, np.zeros((rec, f.channels), dtype=np.float32)))
	outdata[:] = data[:frames]

out_stream = sd.OutputStream(
	callback=ocallback, 
	blocksize=out_blocksize, 
	channels=CHANNELS, 
	samplerate=RATE, 
	dtype=np.float32
)

# DEVICE INPUT

in_volume = 0.0
in_rate = 48000
in_samples = int(in_rate * 1)
in_channels = 1
in_chunksize = 4410
in_stack = AudioStack(in_rate, in_channels, in_chunksize*5)

def icallback(inp, *_):
	global in_volume
	in_stack.push(inp * in_volume)

in_stream = sd.InputStream(
	callback=icallback,
	blocksize=in_chunksize,
	channels=in_channels,
	samplerate=in_rate,
	dtype=np.float32
)
mixer.add(lambda s, r, c, d: in_stack.pull(d).formed(r, c))

def load(name) -> Audio:
	with wave.open(name, 'rb') as wf: return from_wav(wf)

if os.path.exists('data/auto.wav'):
	auto = load('data/auto.wav').flex()
	mixer.add(auto)


# Signal for app stop
# Future that can be awaited, so when Future results (None)
# handlers of it can gracefully shutdown their job
stop_signal: Optional[Future[None]] = None


# CLI TESTING REPL
# loop that waits for stdin input and executes it as python script
def input_loop():
	local = globals()
	print('REPL:\n')
	while True:
		try: exec(input(), None, local)
		except EOFError: break
		except Exception as e: print(e)



# WEBSOCKET SERVER
# New WebSocket client handler
async def ws_open(ws: websockets.ServerConnection):
	path = ws.request.path
	
	match path:
		case '/listen':
			print('WS Opened: listen')
			_rate = RATE
			_channels = CHANNELS
			_chunk_size = 8192
			await ws.send(json.dumps({
				'rate': _rate,
				'channels': _channels,
				'chunkSize': _chunk_size
			}))

			drain = AudioDrain(
				rate=_rate, 
				channels=_channels, 
				samples=_chunk_size, 
				output=lambda f: asyncio.create_task(ws.send(f.data.tobytes())).add_done_callback(lambda _: None)
			)

			_in: MixerOutput = lambda f: drain.push(f.formed(drain.rate, drain.channels))
			mixer.listen(_in)

			try:
				async for msg in ws:
					pass
			except: pass

			print('WS Closed')
			mixer.outputs.remove(_in)
		case '/speak':
			print('WS Opened: speak')
			_rate = RATE
			_channels = CHANNELS

			await ws.send(json.dumps({
				'rate': _rate,
				'channels': _channels
			}))

			stack = AudioStack(
				rate=_rate,
				channels=_channels,
				samples=_rate*4
			)

			_out = lambda s, r, c, d: stack.pull(d).formed(RATE, CHANNELS)
			mixer.add(_out)

			try:
				while True:
					msg = await ws.recv(decode=False)
					data = np.frombuffer(msg, dtype=np.float32).reshape((-1, _channels))
					stack.push(data)
			except: pass

			print('WS Closed')
			mixer.inputs.remove(_in)

# WebSocket server loop
async def ws_serve():
	async with websockets.serve(ws_open, 'localhost', 8765):
		# when this context (async with) ends: websocket server closes
		await stop_signal



# MIXER LIFELOOP
async def mixer_loop():
	last = time.time()
	while True:
		await asyncio.sleep(0.1) # performance delay

		# deltatime calculation
		cur = time.time()
		dt = cur - last
		last = cur

		mixer.tick(dt) # mixing

async def main():
	global stop_signal # import stop_signal variable from global scope
	
	# launch device io streams
	out_stream.start()
	in_stream.start()

	# configure loop, launch app tasks
	loop = asyncio.get_running_loop()
	stop_signal = loop.create_future()

	# run input_loop sync function in separate python executor (thread)
	loop.run_in_executor(None, input_loop)

	# put Coroutine returned by mixer_loop in loop and get Task that gives
	# us ability to control and handle coroutine execution
	# passed name for error logging
	mixing = loop.create_task(mixer_loop(), name='mixer.mixing')
	stop_signal = loop.create_future() # initialize stop_signal
	await ws_serve() # lock main function waiting ws_serve completion

if __name__ == '__main__':
	try:
		# launch default event loop with default configuration
		asyncio.run(main())
	except KeyboardInterrupt as e:
		# handle keyboard Ctrl+C
		print('Stopped: SIGINT')

