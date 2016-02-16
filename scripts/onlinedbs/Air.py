import re
import os
import util
from os.path import join
import numpy as np
import soundfile as sf
import scipy.io

"""
Name: Aachen Impulse Response (AIR) Database

Website: http://www.iks.rwth-aachen.de/de/forschung/tools-downloads/aachen-impulse-response-database/

License: ?

Papers:
Jeub, M., Schäfer, M., Krüger, H., Nelke, C. M., Beaugeant, C. und Vary, P.:
 Download der Veröffentlichung KurzfassungDo We Need Dereverberation for Hand-Held Telephony?,
in: International Congress on Acoustics (ICA), (Sydney, Australia, 23.-27.8.2010), Aug. 2010, ISBN: 978-0-64654-052-8.

Jeub, M., Schäfer, M. und Vary, P.:
 Download der Veröffentlichung Kurzfassung mit ZusatzinformationA Binaural Room Impulse Response Database for the Evaluation of Dereverberation Algorithms,
in: Proceedings of International Conference on Digital Signal Processing (DSP), (Santorini, Greece), IEEE, Juli 2009, S. 1–4, ISBN: 978-1-42443-298-1.
"""

RirTypes = {
	'1': 'binaural',
	'2': 'phone',
}
Distances = {
	'booth': [0.5, 1, 1.5],
	'office': [1, 2, 3],
	'meeting': [1.45, 1.7, 1.9, 2.25, 2.8],
	'lecture': [2.25, 4, 5.56, 7.1, 8.68, 10.2],
	'stairway': [1, 2, 3],
	'aula_carolina': [1, 2, 3, 5, 10, 15, 20],
}

def loadAirRir(filename):
	"""Load a RIR struct from AIR database format. Returns the RIR itself and a dictionary with information about it.

	Possible Dictionary entries (not all must be available)
		fs          Sampling frequency
		rir_type    Type of impulse response
		            '1': binaural (with/without dummy head)
		                  acoustical path: loudspeaker -> microphones
		                  next to the pinna
		            '2': dual-channel (with mock-up phone)
		                 acoustical path: artificial mouth of dummy head
		                 -> dual-microphone mock-up at HHP or HFRP
		mock_up_type   Select mock-up device (for rir_type '2' only)
		                '1': bottom-bottom (BB) (default)
		                '2': bottom-top (BT)
		room        Room type
		            1,2,..,11:  'booth','office','meeting','lecture',
		                         'stairway','stairway1','stairway2',
		                         'corridor','bathroom','lecture1',
		                         'aula_carolina'
		            Available rooms for (1) binaural: 1,2,3,4,5,11
		                                (2) phone: 2,3,4,6,7,8,9,10
		channel     Select channel
		            '0': right; '1': left
		head        Select RIR with or without dummy head
		            (for 'rir_type=1' only)
		            '0': no dummy head; '1': with dummy head
		phone_pos   Position of mock-up phone (for 'rir_type=2' only)
		            '1': HHP (Hand-held), '2': HFRP (Hands-free)
		rir_no      RIR number (increasing distance, for 'rir_type=1' only)
		                Booth:    {0.5m, 1m, 1.5m}
		                Office:   {1m, 2m, 3m}
		                Meeting:  {1.45m, 1.7m, 1.9m, 2.25m, 2.8m}
		                Lecture:  {2.25m, 4m, 5.56m, 7.1m, 8.68m, 10.2m}
		                Stairway: {1m, 2m, 3m}
		                Aula Carolina: {1m, 2m, 3m, 5m, 15m, 20m}
		azimuth     Azimuth angle (0° left, 90° frontal, 180° right)
		                for 'rir_type=1' & 'room=5' -> 0:15:180
		                for 'rir_type=1' & 'room=11'& distance=3 ->0:45:180
	"""
	dic = scipy.io.loadmat(filename, struct_as_record = False)
	x = dic['h_air'][0]
	air_info = dic['air_info'][0][0] # air_info contains some more infos about the RIR
	info = {
		'fs': int(air_info.fs[0][0]),
		'room': str(air_info.room[0]),
		'channel': int(air_info.channel[0][0]),
		'head': int(air_info.head[0][0]),
	}

	# Apparently the struct is no complete and we have to parse further information from the filename
	# rir_type
	m = re.search(r'air_([^_]+)_', filename)
	assert m, 'Could not parse rir_type from filename {}'.format(filename)
	info['rir_type'] = 'binaural' if 'binaural' in util.baseFilename(filename) else 'phone'

	# further parsing depending on rir_type
	if info['rir_type'] == 'binaural': 
		m = re.search(r'air_binaural_' + info['room'] + r'_(\d+)_(\d+)_(\d+)_?([\d_]*).mat', filename)
		assert m, 'Could not parse filename {} (info: {})'.format(filename, info)
		assert int(m.group(1)) == info['channel']
		assert int(m.group(2)) == info['head']
		info['rir_no'] = int(m.group(3))
		if m.group(4): info['azimuth'] = str(m.group(4))
		info['distanceInMeter'] = Distances[info['room']][info['rir_no'] - 1]
	elif info['rir_type'] == 'phone':
		m = re.search(r'air_phone_(.+)_(\w{3,4})_(\d+).mat', filename)
		assert m, 'Could not parse filename {} (info: {})'.format(filename, info)
		
		info['mock_up_type'] = 'BT' if '_BT_' in filename else 'BB'
		if info['mock_up_type'] == 'BT': assert air_info.mock_up_type[0] == 'BT'

		info['phone_pos'] = str(air_info.phone_pos[0])
		assert m.group(2) == info['phone_pos']
	else:
		raise RuntimeError('Unknown rir_type {}'.format(info['rir_type']))

	return x, info


def importRirs(downloadDir, insertIntoDbF):
	url = 'https://www2.iks.rwth-aachen.de/air/air_database_release_1_4.zip'
	filename = join(downloadDir, 'air_1_4.zip')
	unpackDir = join(downloadDir, 'air_1_4')

	dl = util.FileDownloader(url, filename)
	dl.download()
	dl.unpackTo(unpackDir)

	files = []
	for root, dirnames, filenames in os.walk(join(unpackDir, 'AIR_1_4')):
		for filename in filenames:
			if os.path.splitext(filename)[1] != '.mat': continue
			files.append(join(root, filename))

	bar = util.ConsoleProgressBar()
	bar.start('Import AIR')
	for i, file in enumerate(files):
		x, info = loadAirRir(file)
		info['source'] = 'AIR'
		identifier = '{:04d}_{}_{}'.format(i, info['rir_type'][:2], info['room'])
		insertIntoDbF((x, int(info['fs'])), identifier, info)
		bar.progress(i / len(files))
	bar.end()

