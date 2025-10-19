from pathlib import Path
import numpy as np
from wauxio import Audio
import miniaudio
from miniaudio import SampleFormat


def from_mp3(file: Path):
	absol = Path(file).absolute()
	print(absol)
	audio_data = miniaudio.decode_file(absol)
	
	sample_format = audio_data.sample_format
	data = audio_data.samples
	match sample_format:
		case SampleFormat.SIGNED16:
			arr = np.frombuffer(data, np.int16).astype(np.float32) / 2**16
		case SampleFormat.SIGNED32:
			arr = np.frombuffer(data, np.int32).astype(np.float32) / 2**32
		case SampleFormat.UNSIGNED8:
			arr = np.frombuffer(data, np.uint8).astype(np.float32) / 2**8
		case SampleFormat.FLOAT32:
			arr = np.frombuffer(data, np.float32)
		case _:
			raise RuntimeError(f'Unsupported sample format: {sample_format}')

	arr = arr.reshape((-1, audio_data.nchannels))
	
	return Audio(
		data=arr,
		rate=audio_data.sample_rate
	)
