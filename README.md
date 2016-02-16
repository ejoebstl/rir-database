Room Impulse Response (RIR) Database
====================================
Some Python scripts to download and organize RIRs from various online sources. This repository does not provide RIRs. If you use the scripts to obtain RIRs make sure to follow the licenses for the individual collection and be nice by citing there papers ;)

Currently RIRs are collected from:

- [Acoustic Characterisation of Environments (ACE) Corpus](http://www.ee.ic.ac.uk/naylor/ACEweb/index.html)
- [Aachen Impulse Response (AIR) Databas](http://www.iks.rwth-aachen.de/de/forschung/tools-downloads/aachen-impulse-response-database/)
- [Multichannel Acoustic Reverberation Database at York (MARDY) Database](http://www.commsp.ee.ic.ac.uk/~sap/resources/mardy-multichannel-acoustic-reverberation-database-at-york-database/)
- [Database of Omnidirectional and B-Format Impulse Responses](http://isophonics.net/content/room-impulse-response-data-set)
- [RWCP Sound Scene Database](http://www.openslr.org/13/)

Usage example:
```
# This will download all the collections above and copy RIRs to the `wav.imported` folder while putting some infos into `db.json`
python3 scripts/createDb.py --sources=all

# Resample RIRs to 16 kHz, normalize the amplitude and cut silence at the beginning. Results are saved to `wav.normalized`
python3 scripts/normalize.py -fs 16000

# to save some disk space you can delete the downloaded archives
rm -rf download
```