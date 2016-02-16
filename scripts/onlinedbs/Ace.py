import os
import re
import util
import fnmatch
from os.path import join, split

"""
Name: Acoustic Characterisation of Environments (ACE) Corpus

Website: http://www.ee.ic.ac.uk/naylor/ACEweb/index.html

License: Creative Commons Attribution-NoDerivatives 4.0 International License

Paper: J. Eaton, A. H. Moore, N. D. Gaubitch, and P. A. Naylor, “The ACE challenge – corpus description and performance evaluation,” Proc. IEEE Workshop on Applications of Signal Processing to Audio and Acoustics (WASPAA) , New Paltz, NY, USA, Oct. 2015
"""

def importRirs(downloadDir, insertIntoDbF):
	url = 'http://www.commsp.ee.ic.ac.uk/~sap/uploads/data/ACE/ACE_Corpus_RIRN_Single.tbz2'
	filename = join(downloadDir, 'ace.tbz2')
	unpackDir = join(downloadDir, 'ace')

	dl = util.FileDownloader(url, filename)
	dl.download()
	dl.unpackTo(unpackDir)

	files = []
	for root, dirnames, filenames in os.walk(unpackDir):
		for filename in fnmatch.filter(filenames, '*_RIR.wav'):
			files.append(join(root, filename))

	bar = util.ConsoleProgressBar()
	bar.start('Import ACE')
	for i, file in enumerate(files):
		try:
			*_, room, measurement, _ = util.pathParts(file)
		except:
			raise RuntimeError('Could not get room from %s' % file)
		identifier = '{:04d}_{}_{}'.format(i, room.lower(), measurement)
		insertIntoDbF(file, identifier, {
			'source': 'ACE',
			'room': room,
		})
		bar.progress(i / len(files))
	bar.end()



