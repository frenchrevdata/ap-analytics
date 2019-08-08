#!/usr/bin/env python
# -*- coding=utf-8 -*-

"""
Does the majority of the data parsing of the XML files and outputs two critical files -- raw_speeches and speechid_to_speaker.
It also keeps track of errors in the XML files.
"""

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


#Seance followed by less than or equal to 4 line breaks (\n) then date value =
daily_regex = '(?:Séance[\s\S]{0,200}<date value=\")(?:[\s\S]+)(?:Séance[\s\S]{0,200}<date value=\")'
page_regex = '(?:n=\"([A-Z0-9]+)" id="[a-z0-9_]+")\/>([\s\S]{1,9000})<pb '
vol_regex = 'AP_ARTFL_vols\/AP(vol[0-9]{1,2}).xml'
footnote_regex = r'<note place="foot">[\w\W]+<\/note>'

speechid_to_speaker = {}
names_not_caught = set()
speeches_per_day = {}
speakers_using_find = set()
speakers = set()
speaker_num_total_speeches = {}
speaker_num_total_chars = {}
speakers_per_session = {}
global speaker_list

def parseFiles(raw_speeches, multiple_speakers):
	# Assumes all xml files are stored in a Docs folder in the same directory as the python file
    files = os.listdir("AP_ARTFL_vols/")
    dates = set()
    num_sessions = 0
    num_morethan1_session = 0
    for filename in files:
        if filename.endswith(".xml"):
        	print(filename)
        	filename = open('AP_ARTFL_vols/' + filename, "r")
        	# Extracts volume number to keep track of for names_not_caught and speakers_using_find
        	volno = re.findall(vol_regex, str(filename))[0]
        	contents = filename.read()
        	soup = BeautifulSoup(contents, 'lxml')
        	pages = re.findall(page_regex, contents)
        	# Find all the sessions in the xml
        	sessions = soup.find_all(['div3'], {"type": ["other"]})
        	sessions_other = soup.find_all(['div2'], {"type": ["session"]})
        	sessions = sessions + sessions_other
        	# sessions = soup.find_all(['div2', 'div3'], {"type": ["session", "other"]})

        	for session in sessions:
		        date = extractDate(session)
		        # Restricts to valid dates we want to look at
		        if (date >= "1789-05-05") and (date <= "1795-01-04") and (date != "error"):
		        	# Datas is a dataset keeping track of dates already looked at
		        	# Accounts for multiple sessions per day
		        	num_sessions += 1
		        	if date in dates:
		        		num_morethan1_session += 1
		        		date = date + "_soir"
		        		if date in dates:
		        			date = date + "2"
		        			findSpeeches(raw_speeches, multiple_speakers, session, date, volno)
		        		else:
		        			findSpeeches(raw_speeches, multiple_speakers, session, date, volno)
		        			dates.add(date)		        		
		        	else:
		        		findSpeeches(raw_speeches, multiple_speakers, session, date, volno)
		        		dates.add(date)
	        filename.close()
	
	store_to_pickle(num_sessions, "num_sessions.pickle")
	store_to_pickle(num_morethan1_session, "num_morethan1_session.pickle")


def findSpeeches(raw_speeches, multiple_speakers, daily_soup, date, volno):
	id_base = date.replace("/","_")
	number_of_speeches = 0
	presidents = [">le President", "Le President", "Mle President", "President", "le' President", "Le Preesident", "Le Preseident", "Le Presidant", "Le Presideait", "le Presiden", "le President", "Le president", "le president", "Le President,", "Le Presideut", "Le Presidtent", "le Presient", "le Presldent", "le'President"]
	for talk in daily_soup.find_all('sp'):
		# Tries to extract the speaker name and edits it for easier pairing with the Excel file
		try:
			speaker = talk.find('speaker').get_text()
			speaker = remove_diacritic(speaker).decode('utf-8')
			speaker = speaker.replace(".","").replace(":","").replace("MM ", "").replace("MM. ","").replace("M ", "").replace("de ","").replace("M. ","").replace("M, ","").replace("M- ","").replace("M; ","").replace("M* ","")
			if speaker.endswith(","):
				speaker = speaker[:-1]
			if speaker.endswith(", "):
				speaker = speaker[:-1]
			if speaker.startswith(' M. '):
				speaker = speaker[3:]
			if speaker.startswith(' '):
				speaker = speaker[1:]
			if speaker.endswith(' '):
				speaker = speaker[:-1]
		except AttributeError:
			speaker = ""

		while talk.find("note"):
			ftnotes = talk.note.extract()

		# Piece together full speech if in multiple paragraph tags
		speech = talk.find_all('p')
		text = ""
		full_speech = ""
		for section in speech:
			text = text + " " + section.get_text()
		full_speech = remove_diacritic(text).decode('utf-8')
		full_speech = re.sub(r'\([0-9]{1,3}\)[\w\W]{1,100}', ' ', full_speech)
		full_speech = full_speech.replace("\n"," ").replace("--"," ").replace("!"," ")
		full_speech = re.sub(r'([ ]{2,})', ' ', full_speech)
		full_speech = re.sub(r'([0-9]{1,4})', ' ', full_speech)
		# Speaker name is set to the full speaker name extracted from the Excel file
		speaker_name = ""

		#####
		# THIS IS THE INITIAL ATTEMPT AT SPEAKER DISAMBIGUATION
		# Only look at speeches not form the president
		if speaker not in presidents:
			if speaker in speaker_list.index.values:
				for j, name in enumerate(speaker_list.index.values):
					if speaker == name:
						speaker_name = speaker_list["FullName"].iloc[j]
			else:
				for i, name in enumerate(speaker_list['LastName']):
					# Ensures not looking at a list of speakers
					if (speaker.find(",") == -1) and (speaker.find(" et ") != -1):
						#only store multiple speakers when length of speech greater than 100
						speaker_name = "multi"
						if len(full_speech) >= 100:
							multiple_speakers[speaker] = [full_speech, str(volno), str(date)]
					else:
						# Looks if speaker name embedded in any names in the Excel file
						if speaker.find(name) != -1 :
							speaker_name = speaker_list["FullName"].iloc[i]
							# Adds the speakers_using_find list to do a manual check to ensure that no names are mischaracterized
							speakers_using_find.add(speaker + " : " + remove_diacritic(speaker_name).decode('utf-8') + "; " + str(volno) + "; " + str(date) + "\n")
		else:
			speaker_name = "president"
		# Creates the unique speech id
		if (speaker_name is not "") and (speaker_name is not "multi") and (speaker_name is not "president"):
			speaker_name = remove_diacritic(speaker_name).decode('utf-8')
			number_of_speeches = number_of_speeches + 1
			if(speaker_name in speaker_num_total_speeches):
				speaker_num_total_speeches[speaker_name] = speaker_num_total_speeches[speaker_name] + 1
			else:
				speaker_num_total_speeches[speaker_name] = 1
			if(speaker_name in speaker_num_total_chars):
				speaker_num_total_chars[speaker_name] = speaker_num_total_chars[speaker_name] + len(full_speech)
			else:
				speaker_num_total_chars[speaker_name] = len(full_speech)
			if id_base in speakers_per_session:
				speakers_per_session[id_base].add(speaker_name)
			else:
				speakers_per_session[id_base] = set()
				speakers_per_session[id_base].add(speaker_name)
			speakers.add(speaker_name)
			speech_id = "" + id_base + "_" + str(number_of_speeches)
			speechid_to_speaker[speech_id] = speaker_name
			raw_speeches[speech_id] = full_speech
		else:
			if (speaker_name is not "multi") and (speaker_name is not "president"):
				names_not_caught.add(speaker + "; " + str(volno) + "; " + str(date) + "\n")

	speeches_per_day[id_base] = number_of_speeches


# Parses dates from file being analyzed
def extractDate(soup_file):
	dates = soup_file.find_all('date')
	relevant_dates = []
	for date in dates:
		if date.attrs:
			relevant_dates.append(date)
	if (len(relevant_dates) > 0):
		return(relevant_dates[0]['value'])
	else:
		return("error")

if __name__ == '__main__':
	import sys
	speaker_list = load_speakerlist('Copy of AP_Speaker_Authority_List_Edited_3.xlsx')

	raw_speeches = {}
	multiple_speakers = {}
	parseFiles(raw_speeches, multiple_speakers)

	# Writes data to relevant files
	# txtfile = open("names_not_caught.txt", 'w')
	# for name in sorted(names_not_caught):
	# 	txtfile.write(name)
	# txtfile.close()

	# file = open('speakers_using_find.txt', 'w')
	# for item in sorted(speakers_using_find):
	# 	file.write(item)
	# file.close()

	file = open('speakers.txt', 'w')
	for item in sorted(speakers):
		file.write(item + "\n")
	file.close()

	store_to_pickle(speechid_to_speaker, "speechid_to_speaker.pickle")
	store_to_pickle(raw_speeches, "raw_speeches.pickle")
	store_to_pickle(multiple_speakers, "multiple_speakers.pickle")

	store_to_pickle(speaker_num_total_speeches, "speaker_num_total_speeches.pickle")
	store_to_pickle(speaker_num_total_chars, "speaker_num_total_chars.pickle")
	store_to_pickle(speakers, "speakers.pickle")
	store_to_pickle(speeches_per_day, "speeches_per_session.pickle")
	store_to_pickle(speakers_per_session, "speakers_per_session.pickle")

	write_to_csv(speechid_to_speaker, "speechid_to_speaker.csv")
	write_to_csv(raw_speeches, "raw_speeches.csv")
	write_to_csv(speaker_num_total_speeches, "speaker_num_total_speeches.csv")
	write_to_csv(speaker_num_total_chars, "speaker_num_total_chars.csv")
	write_to_csv(speeches_per_day, "speeches_per_day.csv")
	write_to_csv(multiple_speakers, "multiple_speakers.csv")

    
       
   	
