#!/usr/bin/env python
# -*- coding=utf-8 -*-

"""
Creates a mapping of bigram to speechid and number of occurrences in that given speech.
"""

import unicodedata
import csv
import pickle
import regex as re
import pandas as pd
from pandas import *
import numpy as np
import collections
from collections import Counter
import os
from make_ngrams import compute_ngrams
import math
from collections import defaultdict
from processing_functions import write_to_excel, load_list, process_excel, remove_diacritic, compute_tfidf, normalize_dicts

date_regex = '([0-9]{4}-[0-9]{2}-[0-9]{1,2})'

# Maintains the number of documents a given bigram is spoken in for use with tf-idf
#bigram_doc_freq = defaultdict(lambda: 0)


def aggregate(speakers_to_analyze, raw_speeches, speechid_to_speaker):
	speakers_to_consider = []
	speaker_bigram_frequencies = {}

	for speaker in speakers_to_analyze.index.values:
		speakers_to_consider.append(remove_diacritic(speaker).decode('utf-8'))


	for speaker_name in speakers_to_consider:
		print speaker_name
		speaker_bigram_frequencies = {}
		party = speakers_to_analyze.loc[speaker_name, "Party"]
		speech = Counter()
		for identity in raw_speeches:
			date = re.findall(date_regex, str(identity))[0]
			if (date >= "1792-09-20") and (date <= "1793-06-02") and (speaker_name == speechid_to_speaker[identity]):

				indv_speech_bigram = compute_ngrams(raw_speeches[identity], 2)

				for bigram in indv_speech_bigram:
					if bigram in speaker_bigram_frequencies:
						#speechid_frequencies = speaker_bigram_frequencies[bigram]
						#speechid_frequencies[speechid] = indv_speech_bigram[bigram]
						speaker_bigram_frequencies[bigram][identity] = indv_speech_bigram[bigram]
					else:
						speaker_bigram_frequencies[bigram] = {}
						speaker_bigram_frequencies[bigram][identity] = indv_speech_bigram[bigram]
		filename_pickle = "" + speaker_name + "bigram_frequencies.pickle"
		with open(filename_pickle, 'wb') as handle:
			pickle.dump(speaker_bigram_frequencies, handle, protocol = 0)
		filename_csv = "" + speaker_name + "bigram_frequencies.csv"
		w = csv.writer(open(filename_csv, "w"))
		for key, val in speaker_bigram_frequencies.items():
			w.writerow([key,val])


if __name__ == '__main__':
    import sys
    raw_speeches = pickle.load(open("raw_speeches.pickle", "rb"))
    speechid_to_speaker = pickle.load(open("speechid_to_speaker.pickle", "rb"))
    speakers_to_analyze = load_list("Girondins and Montagnards New Mod Limit.xlsx")
    aggregate(speakers_to_analyze, raw_speeches, speechid_to_speaker)
