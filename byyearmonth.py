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

	year_month = {}
	byyearmonth = {}

	ngrams = {}

	raw_speeches = pickle.load(open("raw_speeches.pickle", "rb"))

	for speechid in raw_speeches:
		fulldate = speechid[0:10]
		if (fulldate >= "1792-06-10") and (fulldate <= "1793-08-02"):
			speech_bigrams = compute_ngrams(raw_speeches[speechid], 2)

			yearmonth = speechid[0:7]
			print yearmonth
			if yearmonth in byyearmonth:
				byyearmonth[yearmonth] = byyearmonth[yearmonth] + speech_bigrams
			else:
				byyearmonth[yearmonth] = speech_bigrams
			speech_bigrams = None


			#year_month[speechid] = yearmonth
			#byyearmonth[speechid] = speech_bigrams
	print "here"

	with open("byyearmonth.pickle", "wb") as handle:
		pickle.dump(byyearmonth, handle, protocol = 0)

	w = csv.writer(open("byyearmonth.csv", "w"))
	for key, val in byspeaker.items():
		w.writerow([key, val])

	"""byyearmonth = pd.DataFrame.from_dict(byyearmonth, orient = "index")

	write_to_excel(byyearmonth, "byyearmonth.xlsx")"""
	


if __name__ == '__main__':
	import sys
	firststep()