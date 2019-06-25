#!/usr/bin/env python
# -*- coding=utf-8 -*-

from bs4 import BeautifulSoup
import unicodedata
import os
import csv
import pickle
import regex as re
import pandas as pd
import numpy as np
from nltk import word_tokenize
from nltk.util import ngrams
import collections
from collections import Counter
import os
import gzip
from make_ngrams import compute_ngrams
import xlsxwriter
from processing_functions import remove_diacritic, load_speakerlist


if __name__ == '__main__':
    import sys
    speechid_to_speaker = pickle.load(open("speechid_to_speaker.pickle", "rb"))
    speeches_per_session = pickle.load(open("speeches_per_session.pickle", "rb"))
    speakers_per_session = pickle.load(open("speakers_per_session.pickle", "rb"))
    # num sessions per year
    # SEE BELOW

    # num total speeches
    num_total_speeches = 0
    for session in speeches_per_session:
    	num_total_speeches += speeches_per_session[session]
    file = open('num_total_speeches.txt', 'w')
    file.write(str(num_total_speeches))
    file.close()

    # average number of speeches per session
    numerator = 0
    count = len(speeches_per_session)
    for session in speeches_per_session:
    	numerator += speeches_per_session[session]
    avg_num_speeches_per_session = numerator/(1.0*count)
    file = open('avg_num_speeches_per_session.txt', 'w')
    file.write(str(avg_num_speeches_per_session))
    file.close()

    # average number of speeches per session per year
    """eighty_nine = []
    eighty_nine_num = 0
    ninety = []
    ninety_num = 0
    ninety_one = []
    ninety_one = 0
    ninety_two = []
    ninety_two = 0
    ninety_three = []
    ninety_four = []
    ninety_five = []

    if year == "1789":
    		eighty_nine.append(speeches_per_session[])
    	elif year == "1790":
    	elif year == "1791":
    	elif year == "1792":
    	elif year == "1793":
    	elif year == "1794":
    	else:"""

    num_speeches_per_year = {}
    count_sessions = {}
    for session in speeches_per_session:
    	year = session[0:4]
    	if year in num_speeches_per_year:
    		num_speeches_per_year[year] = num_speeches_per_year[year] + speeches_per_session[session]
    	else:
    		num_speeches_per_year[year] = speeches_per_session[session]

    	if year in count_sessions:
    		count_sessions[year] = count_sessions[year] + 1
    	else:
    		count_sessions[year] = 1

    avg_num_speeches_per_session_per_year = {}
    for year in num_speeches_per_year:
    	avg_num_speeches_per_session_per_year[year] = num_speeches_per_year[year]/(1.0*count_sessions[year])

    w = csv.writer(open("num_speeches_per_year.csv", "w"))
    for key, val in num_speeches_per_year.items():
    	w.writerow([key, val])

    pickle_filename = "num_speeches_per_year.pickle"
    with open(pickle_filename, 'wb') as handle:
    	pickle.dump(num_speeches_per_year, handle, protocol = 0)

    w = csv.writer(open("avg_num_speeches_per_session_per_year.csv", "w"))
    for key, val in avg_num_speeches_per_session_per_year.items():
    	w.writerow([key, val])

    w = csv.writer(open("count_sessions.csv", "w"))
    for key, val in count_sessions.items():
    	w.writerow([key, val])

    pickle_filename = "count_sessions.pickle"
    with open(pickle_filename, 'wb') as handle:
    	pickle.dump(count_sessions, handle, protocol = 0)
    	

    # num speakers per year
    speakers_per_year = {}
    for speechid in speechid_to_speaker:
    	year = speechid[0:4]
    	speaker = speechid_to_speaker[speechid]
    	if year in speakers_per_year:
    		speakers_per_year[year].add(speaker)
    	else:
    		speakers_per_year[year] = set()
    		speakers_per_year[year].add(speaker)
    num_speakers_per_year = {}
    for year in speakers_per_year:
    	num_speakers_per_year[year] = len(speakers_per_year[year])

    w = csv.writer(open("num_speakers_per_year_byspeechid.csv", "w"))
    for key, val in num_speakers_per_year.items():
    	w.writerow([key, val])


    # average number of speakers per session per year
    num_speakers_per_session_per_year = {}
    num_speakers_per_session = {}
    for session in speakers_per_session:
    	year = session[0:4]
    	num_speakers_per_session[session] = len(speakers_per_session[session])
    	if year in num_speakers_per_session_per_year:
    		num_speakers_per_session_per_year[year] = num_speakers_per_session_per_year[year] + len(speakers_per_session[session])
    	else:
    		num_speakers_per_session_per_year[year] = len(speakers_per_session[session])

    avg_num_speakers_per_session_per_year = {}
    for year in num_speakers_per_year:
    	avg_num_speakers_per_session_per_year[year] = num_speakers_per_year[year]/(1.0*count_sessions[year])

    w = csv.writer(open("num_speakers_per_session_per_year.csv", "w"))
    for key, val in num_speakers_per_session_per_year.items():
    	w.writerow([key, val])

    w = csv.writer(open("num_speakers_per_session.csv", "w"))
    for key, val in num_speakers_per_session.items():
    	w.writerow([key, val])


    pickle_filename = "num_speakers_per_year.pickle"
    with open(pickle_filename, 'wb') as handle:
    	pickle.dump(num_speakers_per_year, handle, protocol = 0)

    w = csv.writer(open("avg_num_speakers_per_session_per_year.csv", "w"))
    for key, val in avg_num_speakers_per_session_per_year.items():
    	w.writerow([key, val])


