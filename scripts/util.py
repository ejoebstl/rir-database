import os
import sys
import urllib.request
import patoolib
import shutil
import numpy as np
from scikits.samplerate import resample

class ConsoleProgressBar:
	def __init__(self):
		self.lastMsgLength = 0


	def start(self, title):
		"""Creates a progress bar 50 chars long on the console and moves cursor back to beginning with BS character"""
		sys.stdout.write(title + ' [' + ' ' * 50 + ']' + chr(8) * 52)
		sys.stdout.flush()


	def progress(self, progress, msg=None):
		x = int(50 * progress)
		y = 50 - x - 1
		s = '[{}>{}] {:.1f} %'.format('=' * x, ' ' * y, 100 * progress)
		if msg is not None:
			msg = str(msg)
			if len(msg) > self.lastMsgLength:
				self.lastMsgLength = len(msg)
			else:
				msg = msg + ' ' * (self.lastMsgLength - len(msg))
			s += ' ' + msg
		sys.stdout.write(s + chr(8) * len(s))
		sys.stdout.flush()


	def end(self):
		"""End of progress bar;	Write full bar, then move to next line"""
		sys.stdout.write('[' + '=' * 50 + '] 100.0 %  \n')
		sys.stdout.flush()


class FileDownloader:
	def __init__(self, url, filename):
		self.url = url
		self.filename = filename
		self.title = os.path.basename(filename)


	def download(self, *, showProgress=True, useCache=True):
		if useCache and os.path.isfile(self.filename):
			print('Using cached %s' % self.title)
			return

		bar = ConsoleProgressBar()
		def reportProgress(blocksTransfered, blockSize, totalSize):
			bar.progress((blocksTransfered * blockSize) / totalSize)

		bar.start('Download %s' % self.title)
		urllib.request.urlretrieve(self.url, self.filename, reporthook=reportProgress)
		bar.end()


	def unpackTo(self, outdir):
		# if directory exists and has files we assume that we already successfully extracted the archive
		if os.path.isdir(outdir):
			for dirpath, dirnames, files in os.walk(outdir):
				if len(files): return

		# make sure the outdir exists, but is empty
		createDirectory(outdir, deleteBefore=True)
		try:
			patoolib.extract_archive(self.filename, outdir=outdir)
		except:
			shutil.rmtree(outdir)
			raise


def baseFilename(path):
	return os.path.splitext(os.path.basename(path))[0]


def pathParts(path):
	parts = []
	while 1:
		path, folder = os.path.split(path)
		if folder != '':
			parts.append(folder)
		if path == '':
			return parts[::-1]


def createDirectory(dir, deleteBefore=False):
	if deleteBefore and os.path.isdir(dir):
		shutil.rmtree(dir)
	if not os.path.isdir(dir):
		os.makedirs(dir)


def adjustSampling(x, SourceFs, TargetFs):
	if SourceFs != TargetFs:
		x = resample(x, TargetFs / SourceFs, 'sinc_best')
	return (x, TargetFs)


def trimSilence(x, relMaxSilentAmplitude=0.005, *, trimLeft=True, trimRight=True):
	maxSilentAmplitude = max(abs(x)) * relMaxSilentAmplitude
	indices = np.where(abs(x) > maxSilentAmplitude)[0]
	assert len(indices) > 1
	l = indices[0] if trimLeft else 0
	r = indices[-1] if trimRight else len(x) - 1
	return x[l:r]


def normalizeAmplitude(x):
	if x.dtype == np.int16:
		x = x.astype(np.float32) / max(abs(x))
		return (2**15 * x).astype(np.int16)
	elif x.dtype == np.float32:
		return x / max(abs(x))
	else:
		raise ValueError('Unsupported dtype %s', np.dtype)

