#!/usr/bin/env python

import pickle
import csv
import pandas as pd
from pandas import *
import collections
from collections import Counter
import regex as re
from make_ngrams import compute_ngrams
import math
from processing_functions import load_list, load_speakerlist, process_excel, remove_diacritic, compute_tfidf, normalize_dicts, write_to_excel, convert_keys_to_string, compute_difference, cosine_similarity
from scipy import spatial


def firststep():

	byspeaker = {}
	speakerdict = {}

	byspeaker_allspeakers = {}
	speakerdict_allspeakers = {}

	ngrams = {}

	speakers_to_consider = []


	raw_speeches = pickle.load(open("raw_speeches.pickle", "rb"))
	# dataframe = pd.DataFrame.from_dict(raw_speeches, orient = "index")
	# dataframe.columns = ['Speeches']
	speechid_to_speaker = pickle.load(open("speechid_to_speaker.pickle", "rb"))
	# file = open('num_speeches.txt', 'r')
	# num_speeches = int(file.read())
	# doc_freq = pickle.load(open("bigram_doc_freq.pickle", "rb"))
	speakers_to_analyze = load_list("Girondins and Montagnards New Mod.xlsx")

	for speaker in speakers_to_analyze.index.values:
		speakers_to_consider.append(remove_diacritic(speaker).decode('utf-8'))

	for speechid in raw_speeches:
		fulldate = speechid[0:10]
		if (fulldate >= "1792-09-20") and (fulldate <= "1793-06-02"):
			speech_bigrams = compute_ngrams(raw_speeches[speechid], 2)

			speaker = speechid_to_speaker[speechid]

			print speaker

			if speaker in byspeaker_allspeakers:
				byspeaker_allspeakers[speaker] = byspeaker_allspeakers[speaker] + speech_bigrams
			else:
				byspeaker_allspeakers[speaker] = speech_bigrams
			speech_bigrams = None

	with open("byspeaker_allspeakers.pickle", "wb") as handle:
		pickle.dump(byspeaker_allspeakers, handle, protocol = 0)

	w = csv.writer(open("byspeaker_allspeakers.csv", "w"))
	for key, val in byspeaker.items():
		w.writerow([key, val])

	"""byspeaker_allspeakers = pd.DataFrame.from_dict(byspeaker_allspeakers, orient = "index")

	write_to_excel(byspeaker_allspeakers, "byspeaker_allspeakers.xlsx")"""



if __name__ == '__main__':
	import sys
	firststep()