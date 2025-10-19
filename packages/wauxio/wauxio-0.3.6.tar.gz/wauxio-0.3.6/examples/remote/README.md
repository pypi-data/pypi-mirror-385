
# Remote
This is simple example of how to perform audio processing on server using wauxio and interact with it in network using browser api


## Installation
To install create virtualenv and install all dependencies, run the setup script corresponding to your OS

### Linux
```sh
chmod +x setup.sh
./setup.sh
```

### Windows
```sh
./setup.bat
```


## Run
To run example just run in venv `remote.py` python script
```sh
.venv/Scripts/activate # if not in venv
python remote.py
```

### STDIN REPL (NEW API)
```py
# Example
frame = storage.get('swalk') # read wave file and build AudioFrame (if hide_ext is False in storage init, provide name with extension 'swalk.wav')
reader = AudioReader(frame) # create FrameFlex (AudioFrame read stream)

# pass reader to mixer, so it will start playback in next tick
mixer.add(reader)
```

### STDIN REPL
You can interact with app using stdin (terminal) Python REPL.

```py
# Example
frame = load('data/my_audio.wav') # read wave file and build AudioFrame
flex = frame.flex() # create FrameFlex (AudioFrame read stream)

# pass FrameFlex to mixer, so it will start playback in next tick
mixer.add(flex)
```

**Note**: optional audio file `data/auto.wav` plays on startup.

There's FileSoundStorage mounted at `./data` folder, which decodes every wave file in mounted folder and stores it in memory, so you can quickly access them from store.
```py
# Note: in storage all sounds are named without their real extension (.wav or other)
my_song = store.get('my_song') # real path data/sounds/my_song.wav
my_song_flex = my_song.flex()
mixer.add(my_song_flex)
```

You can change, mute/unmute volume of input (default muted 0.0) and output (default 1.0)
```py
out_volume = 0.5 # decrease device output volume
in_volume = 1.0 # unmute device input
```

### Browser
You can listen/speak to Python server using browser, just open remote.html in your browser.


## Dependencies
- `numpy` for multidimensional numeric arrays
- `wave` for reading audio files of wave format
- `sounddevice` for direct device audio output and input
- `websockets` for serving WebSocket protocol

### Websockets
This example for serving WebSocket protocol in Python uses `websockets` library, which is licensed under the **BSD-3-Clause license**, see more on https://github.com/python-websockets/websockets.
