#!/usr/bin/env python

""" Aggregates information by speaker """

import pickle
import csv
import collections
from collections import Counter
import regex as re
from make_ngrams import compute_ngrams
import math
from processing_functions import load_list, remove_diacritic, write_to_excel, store_to_pickle, write_to_csv
from scipy import spatial


def aggregate_by_speaker():

	byspeaker = {}
	speakerdict = {}

	ngrams = {}

	speakers_to_consider = []


	raw_speeches = pickle.load(open("raw_speeches.pickle", "rb"))
	speechid_to_speaker = pickle.load(open("speechid_to_speaker.pickle", "rb"))
	speakers_to_analyze = load_list("Girondins and Montagnards New Mod Limit.xlsx")
	speaker_num_words = {}

	for speaker in speakers_to_analyze.index.values:
		speakers_to_consider.append(remove_diacritic(speaker).decode('utf-8'))

	for speechid in raw_speeches:
		fulldate = speechid[0:10]
		if (fulldate >= "1792-09-20") and (fulldate <= "1793-06-02"):
			num_words = len(raw_speeches[speechid].split())
			speech_bigrams = compute_ngrams(raw_speeches[speechid], 2)

			speaker = speechid_to_speaker[speechid]

			if speaker in speaker_num_words:
				speaker_num_words[speaker] += num_words
			else:
				speaker_num_words[speaker] = num_words
			
			if speaker in speakers_to_consider:
				if speaker in byspeaker:
					byspeaker[speaker] = byspeaker[speaker] + speech_bigrams
				else:
					byspeaker[speaker] = speech_bigrams
			speech_bigrams = None

	write_to_csv(byspeaker)
	store_to_pickle(byspeaker)

	write_to_csv(speaker_num_words)
	store_to_pickle(speaker_num_words)


if __name__ == '__main__':
	import sys
	aggregate_by_speaker()