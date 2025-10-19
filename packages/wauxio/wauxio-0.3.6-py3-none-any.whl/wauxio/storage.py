import asyncio
from dataclasses import dataclass
from pathlib import Path, PurePath
from typing import Callable, Coroutine, Optional

from wauxio import Audio

CodecType = Callable[[Path], Coroutine[None, None, Audio]]
SyncCodecType = Callable[[Path], Audio]

@dataclass
class _Codec:
	callback: CodecType | SyncCodecType
	sync: bool



def _nameptr_to_fsptr(name: str, hide_ext: bool = False) -> str:
	if hide_ext:
		last = name[-1] if name != '' else ''
		if last != '*' and last != '/': name += '.*'
	return name

def _fs_to_name(path: Path, root: Path, hide_ext: bool = False) -> str:
	if hide_ext: path = path.with_suffix('')
	return path.relative_to(root).as_posix()


class FileSoundStorage:
	root: Path
	sounds: dict[str, Audio]
	codecs: dict[str, _Codec]
	lock: asyncio.Lock
	hide_ext: bool

	def __init__(self, root: Path, hide_ext: bool = False):
		super().__init__()
		
		self.root = root
		self.hide_ext = hide_ext

		self.sounds = dict()
		self.codecs = dict()
		self.lock = asyncio.Lock()
	
	def mount_sync(self, *paths: str):
		if paths == (): paths = ('**/*',)
		checked_sounds: set[str] = set()
		sounds = self.sounds
		codecs = self.codecs
		wildcard_codec = codecs.get('*', None)
		hide_ext = self.hide_ext
		root = self.root
		for nameptr in paths:
			# clear cached sounds
			for name in sounds.keys():
				if name not in checked_sounds and Path(name).match(nameptr):
					sounds.pop(name)
			
			fsptr = _nameptr_to_fsptr(nameptr, hide_ext)
			# load new sounds
			for path in root.glob(fsptr):
				if not path.is_file(): continue
				name = _fs_to_name(path, root, hide_ext)
				if name in checked_sounds: continue
				codec = codecs.get(path.suffix, None) or wildcard_codec
				if not codec: continue
				if codec.sync:
					checked_sounds.add(name)
					sounds[name] = codec.callback(path)
	
	async def mount(self, *paths: str):
		if paths == (): paths = ('**/*',)
		await self.lock.acquire()

		checked_sounds: set[str] = set()
		sounds = self.sounds
		codecs = self.codecs
		wildcard_codec = codecs.get('*', None)
		hide_ext = self.hide_ext
		root = self.root
		async def _load(path: Path, codec: _Codec):
			name = _fs_to_name(path, hide_ext)
			sounds[name] = await codec.callback(path)
		
		async with asyncio.TaskGroup() as tg:
			for nameptr in paths:
				# clear cached sounds
				for name in sounds.keys():
					if Path(name).match(nameptr) and name not in checked_sounds:
						sounds.pop(name)
				
				fsptr = _nameptr_to_fsptr(nameptr, hide_ext)
				# load new sounds
				for path in root.glob(fsptr):
					if path.is_file():
						name = _fs_to_name(path, root, hide_ext)
						if name in checked_sounds: continue
						codec = codecs.get(path.suffix, None) or wildcard_codec
						if not codec: continue
						checked_sounds.add(name)
						if codec.sync:
							sounds[name] = codec.callback(path)
						else:
							tg.create_task(_load(path, codec))
		
		self.lock.release()
	
	def use_codec(self, ext: str, callback: CodecType):
		self.codecs[ext] = _Codec(callback, False)

	def use_sync_codec(self, ext: str, callback: SyncCodecType):
		self.codecs[ext] = _Codec(callback, True)
	
	def get(self, name: str) -> Optional[Audio]:
		return self.sounds.get(name, None)

