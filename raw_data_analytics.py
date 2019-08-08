#!/usr/bin/env python
# -*- coding=utf-8 -*-

""" Compute raw analytics on xml files """

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
from processing_functions import remove_diacritic, load_speakerlist, store_to_pickle, write_to_csv


if __name__ == '__main__':
    import sys

    # Load relevant files
    speechid_to_speaker = pickle.load(open("speechid_to_speaker.pickle", "rb"))
    speeches_per_session = pickle.load(open("speeches_per_session.pickle", "rb"))
    speakers_per_session = pickle.load(open("speakers_per_session.pickle", "rb"))

    # Mum total speeches
    num_total_speeches = 0
    for session in speeches_per_session:
    	num_total_speeches += speeches_per_session[session]
    file = open('num_total_speeches.txt', 'w')
    file.write(str(num_total_speeches))
    file.close()

    # Average number of speeches per session
    numerator = 0
    count = len(speeches_per_session)
    for session in speeches_per_session:
    	numerator += speeches_per_session[session]
    avg_num_speeches_per_session = numerator/(1.0*count)
    file = open('avg_num_speeches_per_session.txt', 'w')
    file.write(str(avg_num_speeches_per_session))
    file.close()

    # Metrics based on year
    num_speeches_per_year = {}

    # Keeps tracks of the number of sessions per year
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

    store_to_pickle(num_speeches_per_year, "num_speeches_per_year.pickle")
    store_to_pickle(count_sessions, "count_sessions.pickle")

    write_to_csv(num_speeches_per_year, "num_speeches_per_year.csv")
    write_to_csv(avg_num_speeches_per_session_per_year, "avg_num_speeches_per_session_per_year.csv")
    write_to_csv(count_sessions, "count_sessions.csv")
    	

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

    # write_to_csv(num_speakers_per_year_byspeechid, "num_speakers_per_year_byspeechid.csv")

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

    write_to_csv(num_speakers_per_session_per_year, "num_speakers_per_session_per_year.csv")
    write_to_csv(num_speakers_per_session, "num_speakers_per_session.csv")
    store_to_pickle(num_speakers_per_year, "num_speakers_per_year.pickle")
    write_to_csv(avg_num_speakers_per_session_per_year, "avg_num_speakers_per_session_per_year.csv")


