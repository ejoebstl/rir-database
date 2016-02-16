import os
import json
import argparse
import numpy as np
import util

ListDir = 'lists'

class RirSet:
	def __init__(self, name, share = None):
		self.name = name
		self.share = share
		self.rirs = set()

	def __len__(self):
		return len(self.rirs)

	def add(self, rir):
		self.rirs.add(rir)

	def missing(self, totalRirs):
		return len(self.rirs) / totalRirs - self.share

	def save(self, folder):
		filename = os.path.join(folder, self.name + '.rirs')
		with open(filename, 'w') as f:
			f.write('\n'.join(sorted(list(self.rirs))))


def main(dbFilename, maxLenEasy = 2.5):

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
	
	easy = RirSet('train.easy'.format(maxLenEasy))
	hard = RirSet('train.hard'.format(maxLenEasy))
	for rir in sets[0].rirs:
		if rirDb[rir]['length'] > maxLenEasy:
			hard.add(rir)
		else:
			easy.add(rir)
	sets.append(easy)
	sets.append(hard)

	# safe set files
	util.createDirectory(ListDir)
	for s in sets:
		print('{} set: {}'.format(s.name, len(s)))
		s.save(ListDir)



if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Split RIRs into different sets and create a text file with the RIR IDs for each set')
	parser.add_argument('-db', '--database', type=str, default='db.json')
	args = parser.parse_args()
	main(args.database)
