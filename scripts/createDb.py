import os
import re
import argparse
import json
import shutil
import util
import soundfile as sf
from onlinedbs import Ace, Air, Mardy, Omni, Rwcp

DownloadDir = 'download'
ImportDir = 'wav.imported'

def main(dbFilename='db.json', deleteBefore=False, sources=[]):
	# open db
	if os.path.isfile(dbFilename) and not deleteBefore:
		rirDb = json.load(open(dbFilename))
	else:
		rirDb = {}

	util.createDirectory(ImportDir, deleteBefore=deleteBefore)
	util.createDirectory(DownloadDir)

	def insertIntoDb(file, identifier, info):
		onlineDbId = info['source'].lower()
		id = '{}_{}'.format(onlineDbId, identifier)
		if id in rirDb:
			return False
		
		info['id'] = id
		info['filename'] = os.path.join(ImportDir, id + '.wav')
		rirDb[id] = info

		# copy file (or write as wav file)
		if isinstance(file, str):
			shutil.copyfile(file, info['filename'])
		else:
			assert len(file) == 2
			x, fs = file
			sf.write(info['filename'], x, fs)

		return True

	if 'ace' in sources:
		Ace.importRirs(DownloadDir, insertIntoDb)
	if 'air' in sources:
		Air.importRirs(DownloadDir, insertIntoDb)
	if 'mardy' in sources:
		Mardy.importRirs(DownloadDir, insertIntoDb)
	if 'omni' in sources:
		Omni.importRirs(DownloadDir, insertIntoDb)
	if 'rwcp' in sources:
		Rwcp.importRirs(DownloadDir, insertIntoDb)

	# more sources could be found here: http://www.dreams-itn.eu/index.php/dissemination/science-blogs/24-rir-databases

	# save db
	with open(dbFilename, 'w') as dbFile:
		json.dump(rirDb, dbFile, sort_keys=True, indent=4)

	print('Database size: {}'.format(len(rirDb)))


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Create RIR database by importing all RIRs from the known databases')
	parser.add_argument('-db', '--database', type=str, default='db.json')
	parser.add_argument('--deleteBefore', action='store_true', help='Whether to delete old database (and imported data) before')
	parser.add_argument('--sources', type=str, default='mardy,omni', help='Comma separated list of the sources to use (available: ACE, AIR, MARDY, OMNI, RWCP)')
	args = parser.parse_args()
	if args.sources == 'all':
		args.sources = 'ace,air,mardy,omni,rwcp'
	main(args.database, args.deleteBefore, args.sources.lower().split(','))

