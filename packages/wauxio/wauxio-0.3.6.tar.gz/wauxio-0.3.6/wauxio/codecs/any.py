from pathlib import Path
import numpy as np
from wauxio import Audio
import soundfile as sf


def from_any(file: Path):
	audio_data, sr = sf.read(file)
	channels = audio_data.shape[1] if len(audio_data.shape) > 1 else 1
	
	if channels > 1:
		audio_data = audio_data.reshape(-1, channels)
	else:
		audio_data = audio_data.reshape(-1, 1)
	
	return Audio(audio_data.astype(np.float32), sr)
