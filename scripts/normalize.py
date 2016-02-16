from os.path import join, isfile
import argparse
import json
import numpy as np
import soundfile as sf
import shutil
from scikits.samplerate import resample
import util

ImportDir = 'wav.imported'
NormalizeDir = 'wav.normalized'

def main(dbFilename, targetFs, force=False):
	util.createDirectory(NormalizeDir)

	rirDb = json.load(open(dbFilename))

	bar = util.ConsoleProgressBar()
	bar.start('Normalize RIRs')
	i = 0
	for rirId, rir in rirDb.items():
		targetFilename = join(NormalizeDir, rir['id'] + '.wav')
		if not force:
			if rir['filename'] == targetFilename and \
				rir['fs'] == targetFs and \
				targetFilename:
				continue

		x, fs_x = sf.read(join(ImportDir, rir['id'] + '.wav'), dtype='float32')
		y, fs_y = x, fs_x

		if fs_y != targetFs:
			y = resample(y, targetFs / fs_y, 'sinc_best')
			fs_y = targetFs

		rir['length_org'] = len(y) / fs_y
		y = util.trimSilence(y, 0.001, trimRight=False)
		y = util.normalizeAmplitude(y)

		sf.write(targetFilename, y, fs_y)
		
		rir['filename'] = targetFilename
		rir['fs'] = fs_y
		rir['length'] = len(y) / fs_y

		i += 1
		bar.progress(i / len(rirDb))
	bar.end()

	with open(dbFilename, 'w') as dbFile:
		json.dump(rirDb, dbFile, sort_keys=True, indent=4)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Create normalized versions of all RIRs in the database')
	parser.add_argument('-db', '--database', type=str, default='db.json')
	parser.add_argument('-fs', '--samplingrate', type=int, default=16000, help='Target sampling rate in Hz')
	parser.add_argument('-f', '--force', action='store_true', help='By default this script will skip RIRs that were already normalized.')
	args = parser.parse_args()
	main(args.database, args.samplingrate, args.force)
