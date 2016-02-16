import util
from glob import glob
from os.path import join

"""
Name: Database of Omnidirectional and B-Format Impulse Responses

Website: http://isophonics.net/content/room-impulse-response-data-set

Note: 3 big rooms with RIRs meeasured in grids and provided in Omnidirectional and B-Format. We use the omnidirectional version.

License: These IRs are released under the Creative Commons Attribution-Noncommercial-Share-Alike license with attribution to the Centre for Digital Music, Queen Mary, University of London.

Paper: Stewart, Rebecca and Sandler, Mark. "Database of Omnidirectional and B-Format Impulse Responses", in Proc. of IEEE Int. Conf. on Acoustics, Speech, and Signal Processing (ICASSP 2010), Dallas, Texas, March 2010.
"""

OmniRooms = ['greathall', 'octagon', 'classroom']

def importRirs(downloadDir, insertIntoDbF):
	j = 0
	for room in OmniRooms:
		url = 'http://kakapo.dcs.qmul.ac.uk/irs/{}Omni.zip'.format(room)
		filename = join(downloadDir, 'omni.{}.zip'.format(room))
		unpackDir = join(downloadDir, 'omni.{}'.format(room))

		dl = util.FileDownloader(url, filename)
		dl.download()
		dl.unpackTo(unpackDir)

		fileSelector = join(unpackDir, 'Omni', '*.wav')
		files = list(glob(fileSelector))

		bar = util.ConsoleProgressBar()
		bar.start('Import OMNI %s' % room)
		for i, file in enumerate(files):
			identifier = '{:04d}_{}_{}'.format(j, room, util.baseFilename(file))
			j += 1
			insertIntoDbF(file, identifier, {
				'source': 'OMNI',
				'room': room,
			})
			bar.progress(i / len(files))
		bar.end()

