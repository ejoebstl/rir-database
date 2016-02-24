import re
import os
from os.path import join
import numpy as np
import soundfile as sf
import util

"""
Name: RWCP Sound Scene Database

Website: http://www.openslr.org/13/

License: Research and development use only

Paper:
@inproceedings{nakamura2000acoustical,
  title={Acoustical Sound Database in Real Environments for Sound Scene Understanding and Hands-Free Speech Recognition.},
  author={Nakamura, Satoshi and Hiyane, Kazuo and Asano, Futoshi and Nishiura, Takanobu and Yamada, Takeshi},
  booktitle={LREC},
  year={2000}
}
"""

# file format for the room impulse responses according to micarray/indexe.htm
RawFormat = {
	'format': 'RAW',
	'channels': 1,
	'samplerate': 48000, # 48 
	'endian': 'LITTLE', # little ending
	'subtype': 'FLOAT' # 32 bit float (= 4 byte)
}

def importRirs(downloadDir, insertIntoDbF):
	url = 'http://www.openslr.org/resources/13/RWCP.tar.gz'
	filename = join(downloadDir, 'rwcp.tar.gz')
	unpackDir = join(downloadDir, 'rwcp')
	
	dl = util.FileDownloader(url, filename)
	dl.download()
	dl.unpackTo(unpackDir)

	files = []
	for root, dirnames, filenames in os.walk(join(unpackDir, 'RWCP/micarray/MICARRAY/data1')):
		for filename in filenames:
			if filename[-2:] != '.1': continue # we only use the front microphone
			files.append(join(root, filename))

	pattern = re.compile('(circle|cirline)\/(\w{3})\/imp(\d{3})')

	bar = util.ConsoleProgressBar()
	bar.start('Import RWCP')
	for i, file in enumerate(sorted(files)): # we sort to get same identifiers cross-platform
		m = pattern.search(file)
		assert m, 'Could parse room from path ({})'.format(file)
		room = m.group(2)
		identifier = '{:04d}_{}_{}'.format(i, room.lower(), m.group(3))

		x, fs = sf.read(file, dtype='float32', **RawFormat)
		x /= max(abs(x))
		x = (3**15 * x).astype(np.int16)

		insertIntoDbF((x, fs), identifier, {
			'source': 'RWCP',
			'room': room,
		})
		bar.progress(i / len(files))
	bar.end()

