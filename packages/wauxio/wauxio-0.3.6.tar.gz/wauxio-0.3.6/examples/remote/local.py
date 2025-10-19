import asyncio
from asyncio import CancelledError, Task
from pathlib import Path
from typing import Dict, Optional
import numpy as np
import sounddevice as sd

from wauxio import AudioReader, StreamOptions
from wauxio.codecs.any import from_any
from wauxio.codecs.mp3 import from_mp3
from wauxio.mixer import AudioMixer
from wauxio.output import AudioOutput
from wauxio.storage import FileSoundStorage
from wauxio.utils import AudioStack


# mount sound storage and codecs
# it will storage sounds in pure numpy arrays
store = FileSoundStorage(Path('sounds/'), hide_ext=True)
store.use_sync_codec('.wav', from_any)
store.use_sync_codec('.ogg', from_any)
store.use_sync_codec('.mp3', from_mp3)
store.mount_sync()
print('Sounds:', store.sounds)

# Configuration for sd
RATE = 48000
CHANNELS = 2

# init audiomixer and audiooutput
mixer = AudioMixer()
output = AudioOutput(rate=RATE, channels=CHANNELS)
output.connect(mixer)

# output stack -> like sound buffer
out_stack = AudioStack(
    rate=RATE,
    channels=CHANNELS,
    samples=int(RATE*2)
)
output.listen(out_stack.push)

players: Dict[str, AudioReader] = {}
mixing_task: Optional[Task] = None
out_stream: Optional[sd.OutputStream] = None

def out_callback(outdata, frames, time, status):
	duration = frames/RATE
	frame = out_stack.pull(StreamOptions(duration, RATE, CHANNELS))

	audio = frame.audio
	if not audio: return

	data = audio.data
	outdata[:len(data)] = data

def add_sound(name: str):
    '''
    Load sound from storage and set it to player
    Parameters:
        name (str): Sound name
    '''
    
    sound = store.get(name)
    if sound is None:
        print(f'Sound \'{name}\' not found!')
        return
    
    if name in players:
        print(f'Player \'{name}\' already exists!')
        return
    
    player = AudioReader(sound.formed(rate=RATE, channels=CHANNELS))
    players[name] = player
    mixer.add(player)
    print(f'Added sound \'{name}\'')


def set_pitch(name: str, value: float):
    '''
    Set pitch for player
    Parameters:
        name (str): Player name
        value (float): pitch value(0 - pause)
    '''
    if name not in players:
        print(f'Player \'{name}\' not found!')
        return
    
    players[name].pitch = value
    print(f'Player \'{name}\' pitch set to {value}')


def set_position(name: str, seconds: float):
    '''
    Set position for player
    Параметры:
        name (str): Player name
        seconds (float): Position value in seconds
    '''
    if name not in players:
        print(f'Player \'{name}\' not found!')
        return
    
    players[name].position = seconds
    print(f'Player \'{name}\' position set to {seconds}s')


def get_status(name: Optional[str] = None):
    if not players:
        print('No active players')
        return
    
    if name:
        if name not in players:
            print(f'Player \'{name}\' not found!')
            return
        
        p = players[name]
        print(
            f'Player \'{name}\':\n'
            f'  Position: {p.position:.1f}s\n'
            f'  Pitch: {p.pitch}\n'
            f'  Duration: {p.duration:.1f}s'
        )
    else:
        for pid, p in players.items():
            print(
                f'Player \'{pid}\':\n'
                f'  Position: {p.position:.1f}s\n'
                f'  Pitch: {p.pitch}\n'
                f'  Duration: {p.duration:.1f}s\n'
                '―'*30
            )
            

async def main():
    global mixing_task, out_stream
    
    # init audio stream
    out_stream = sd.OutputStream(
        samplerate=RATE,
        blocksize=int(RATE * 0.2),
        channels=CHANNELS,
        dtype=np.float32,
        callback=out_callback
    )
    out_stream.start()
    
    # start mixer loop
    loop = asyncio.get_running_loop()
    mixing_task = loop.run_in_executor(None, output.run_sync, 0.1)
    
    await loop.run_in_executor(None, input_loop)
    
    try:
        await asyncio.gather(mixing_task)
    except CancelledError:
        print('Stopping...')
        out_stream.close()
        output.stop()
        if mixing_task:
            mixing_task.cancel()

def input_loop():
    print('\nAvailable commands:')
    print('add_sound(\'filename\')  - Load sound')
    print('pause()                - Pause playback')
    print('resume()               - Resume playback')
    print('set_position(seconds)  - Set position')
    print('set_pitch(value)       - Set playback speed')
    print('get_status()           - Show current status')
    print('-' * 30)
    
    g = globals()
    while True:
        try:
            command = input('>>> ')
            if not command:
                continue
            exec(command, g, g)
        except (EOFError, KeyboardInterrupt):
            asyncio.get_running_loop().call_soon_threadsafe(
                asyncio.get_running_loop().stop
            )
            break
        except Exception as e:
            print(f'Error: {e}')

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Program terminated')