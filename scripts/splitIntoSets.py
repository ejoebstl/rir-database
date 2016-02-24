import os
import json
import argparse
import numpy as np
import util

ListDir = 'lists'

class RirSet(set):
	def __init__(self, name, share=None):
		self.name = name
		self.share = share

	def missing(self, totalRirs):
		return len(self) / totalRirs - self.share

	def save(self, folder, silent=False):
		if not silent: print('{} set: {} RIRs'.format(self.name, len(self)))
		filename = os.path.join(folder, self.name + '.rirs')
		with open(filename, 'w') as f:
			f.write('\n'.join(sorted(list(self))))

	def load(self, folder):
		filename = os.path.join(folder, self.name + '.rirs')
		with open(filename) as f:
			for line in f:
				self.add(line.strip())


def main(dbFilename):
	print('Splitting RIRs into sets...')
	sets = [
		RirSet('train', 0.8),
		RirSet('test', 0.1),
		RirSet('dev', 0.1),
	]

	# open database
	rirDb = json.load(open(dbFilename))
	rirs = sorted(list(rirDb.keys()))

	# to distribute the RIRs to the set we could to a shuffle, but as they are in alphabetical order and just going over them guaranties that we distribute the different conditions (mostly) equally on the different sets
	sets[0].add(rirs[0])
	for i in range(1, len(rirs)):
		si = np.argmin([s.missing(i) for s in sets])
		sets[si].add(rirs[i])

	# safe set files
	util.createDirectory(ListDir)
	for s in sets:
		s.save(ListDir)


def createMoreLists(dbFilename, maxLenEasy=2.5, room='classroom'):
	print('Creating additional lists...')

	# open database
	rirDb = json.load(open(dbFilename))
	rirs = sorted(list(rirDb.keys()))
	
	train = RirSet('train')
	test = RirSet('test')
	dev = RirSet('dev')
	train.load(ListDir)
	test.load(ListDir)
	dev.load(ListDir)

	print('Splitting train set into hard and easy RIRs according to length.') # TODO: use reverberation time (RT60)
	easy = RirSet('train.easy')
	hard = RirSet('train.hard')
	for rir in rirs:
		if rir in train:
			if rirDb[rir]['length'] > maxLenEasy:
				hard.add(rir)
			else:
				easy.add(rir)
	easy.save(ListDir)
	hard.save(ListDir)

	print('Creating sets containing only OMNI {}.'.format(room))
	roomTrain = RirSet(room + '.train')
	roomTrainSmall = RirSet(room + '.train.small')
	roomTest = RirSet(room + '.test')
	roomDev = RirSet(room + '.dev')
	for i, rir in enumerate(rirs):
		if rir.startswith('omni') and room in rir:
			if rir in train:
				roomTrain.add(rir)
				if i % 10 == 0:
					roomTrainSmall.add(rir)
			elif rir in test:
				roomTest.add(rir)
			else:
				assert rir in dev
				roomDev.add(rir)
	omniListDir = os.path.join(ListDir, 'omni')
	util.createDirectory(omniListDir)
	roomTrain.save(omniListDir)
	roomTrainSmall.save(omniListDir)
	roomTest.save(omniListDir)
	roomDev.save(omniListDir)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Split RIRs into different sets and create a text file with the RIR IDs for each set')
	parser.add_argument('-db', '--database', type=str, default='db.json')
	parser.add_argument('--more', action='store_true')
	args = parser.parse_args()
	main(args.database)
	if args.more:
		createMoreLists(args.database)

