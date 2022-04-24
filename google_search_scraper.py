# coding: utf-8

# ––––––––––––––––––––––––––––––––––––––––––––––––– IMPORT LIBRARIES –––––––––––––––––––––––––––––––––––––––––––––––– #

# TODO: make log file that will keep up with the status of runs, also make a reset Makefile tag for resetting status
# TODO: do like an import check to see what the values of MULTI_RAN or MULTI_SEARCH_DICT is
# TODO: warn the user that they must do those things in order if they are in a reset or beginning state

import re
import sys
import pandas as pd
import itertools 
import urllib.parse
import urllib.request

try: 
		from googlesearch import search 
except ImportError:  
		print("No library named \'google\' found.")
		sys.exit(1)

# ––––––––––––––––––––––––––––––––––––––––––––––––– GLOBAL VARIABLES –––––––––––––––––––––––––––––––––––––––––––––––– #

DATE_THRESHOLD = 2010
INPUT_FILE = "capstone_search_strings.csv"
OUTPUT_FILE = "scraper_results.csv"
ALIAS_CHOP = 0 # if all search strings begin with the same prefixed word, can chop it off for alias naming
NUM_RESULTS = 10
# SEARCH_TIMEOUT = 5

# ––––––––––––––––––––––––––––––––––––––––––––––– PROTOTYPED FUNCTIONS –––––––––––––––––––––––––––––––––––––––––––––– #

def urlify(s):
	# Remove all non-word characters (everything except numbers and letters)
	s = re.sub(r"[^\w\s]", '', s)
	# Replace all runs of whitespace with a single dash
	s = re.sub(r"\s+", '-', s)

	return s


def print_url_list_lengths(mat):
	print("\n")
	total = 0
	for idx in range(len(mat)):
		print("Length of list", str(idx+1) + ':', len(mat[idx]))
		total += len(mat[idx])
	print("Total:", total)

# –––––––––––––––––––––––––––––––––––––––––––––––– PROTOTYPED CLASSES ––––––––––––––––––––––––––––––––––––––––––––––– #

class Dictionary(dict):
	def __init__(self): 
		self = dict() 
		
	def set_dict_entry(self, key, value): 
		self[key] = value

# –––––––––––––––––––––––––––––––––––––––––––––––––– MAIN FUNCTION –––––––––––––––––––––––––––––––––––––––––––––––––– #

def main():

	# ––––––––––––––––––––––––––––––––––––––––––––––––– CHECKING STATUS ––––––––––––––––––––––––––––––––––––––––––––––––– #

	# TODO: check if status.py exists, if it doesnt exist, run reset.py, possibly as child process
	# TODO: check the values of the logged status variables

	# –––––––––––––––––––––––––––––––––––––––––––––––– CMD LINE ARGUMENTS ––––––––––––––––––––––––––––––––––––––––––––––– #

	cli_bools = ["True", "False"]

	temp = sys.argv[1]
	multi = sys.argv[2]
	dupe = sys.argv[3]
	date = sys.argv[4]
	lang = sys.argv[5]
	verbose = int(sys.argv[6])

	if(temp not in cli_bools or multi not in cli_bools or dupe not in cli_bools or date not in cli_bools or lang not in cli_bools):
		print("ERROR 1639: Invalid command line argument booleans.")
		sys.exit(1)

	if(verbose not in [0,1,2]):
		print("ERROR 1639: Invalid command line argument verbosity.")
		sys.exit(1)

	temp = False if temp == "False" else True
	multi = False if multi == "False" else True
	dupe = False if dupe == "False" else True
	date = False if date == "False" else True
	lang = False if lang == "False" else True

	# ––––––––––––––––––––––––––––––––––––––––––––––––– SEARCH STRINGS –––––––––––––––––––––––––––––––––––––––––––––––––– #
	 
	queries = []
	q_df = pd.read_csv(INPUT_FILE)
	for index, row in q_df.iterrows():
		queries.append(row["STRING"])

	# –––––––––––––––––––––––––––––––––––––––––––––––– INDIVIDUAL SEARCH –––––––––––––––––––––––––––––––––––––––––––––––– #

	# Get individual list of 100 results if necessary
	if(temp):
		if(verbose >= 1): print("\nPerforming single search...")
		temp_list = []
		for j in search("SINGLE SEARCH STRING HERE", num_results=NUM_RESULTS, lang="en"):
			temp_list.append(j)
		print(temp_list)

	if(not temp):
		if(verbose >= 1): print("\nSkipping single search...")

	# ––––––––––––––––––––––––––––––––––––––––––––––––––– MULTI SEARCH ––––––––––––––––––––––––––––––––––––––––––––––––– #

	if(multi):
		if(verbose >= 1): print("\nPerforming multi-search...")
		# Create dictionary instance
		search_dict = Dictionary()

		# Initialize dictionary with shortened key & array with [1-based index, actual search string, empty list for URLs]
		if(verbose >= 1): print("Initializing dictionary...")
		for q in range(len(queries)):
			search_dict.set_dict_entry(urlify(queries[q][ALIAS_CHOP:]), [q+1, queries[q], []])

		if(verbose >= 1): print("Populating dictionary with Google search results URLs...")
		for q_idx in range(len(queries)):
			results = []
			for j in search(search_dict[urlify(queries[q_idx][ALIAS_CHOP:])][1], num_results=NUM_RESULTS, lang="en"):
				results.append(j)
			search_dict.set_dict_entry(urlify(queries[q_idx][ALIAS_CHOP:]), [q_idx+1, queries[q_idx], results])
			print(search_dict[urlify(queries[q_idx][ALIAS_CHOP:])], '\n')

		print("Search Dictionary: ", search_dict)


	if(not multi):
		if(verbose >= 1): print("\nSkipping multi-search...")

		# Original dictionary formed from 100 Google search results for 14 search strings
		search_dict = {
			
		}

	# –––––––––––––––––––––––––––––––––––––––––––––––– REMOVE DUPLICATES ––––––––––––––––––––––––––––––––––––––––––––––– #

	search_str_count = len(q_df.index)
	url_mat = [[]] * search_str_count # dynamically sized matrix based on number of search strings in CSV
	santzd_url_mat = [[]] * search_str_count # initialize empty sanitized URL matrix
	print("Number of search strings: ", search_str_count)

	# Remove all duplicates from the original dictionary
	if(dupe):
		if(verbose >= 1): print("\nRemoving duplicate URLs...")
		
		# Move URL list data from dictionary to <url_mat>
		for key in search_dict:
			url_mat[search_dict[key][0]-1] = search_dict[key][2]

		# Removes duplicates from own lists, makes new URL matrix
		for count in range(len(url_mat)):
			santzd_url_mat[count] = list(set(url_mat[count]))

		# Removes duplicates from all other lists
		for lst in santzd_url_mat:
			for l in santzd_url_mat:
				if(lst == l): continue # if previous loops index the same list
				for elem in l:
					if(elem in lst):
						l.remove(elem) # remove duplicate

	# URL matrix after removing duplicates
	if(not dupe):
		if(verbose >= 1): print("\nSkipping duplicate removal...")
		santzd_url_mat = [
						
		]

	# Length of each list after removing duplicates
	if(verbose >= 2): print(santzd_url_mat)
	if(verbose >= 1): print_url_list_lengths(santzd_url_mat)

	# –––––––––––––––––––––––––––––––––––––––––––––––––– DATE FILTERING ––––––––––––––––––––––––––––––––––––––––––––––––– #

	if(date):
		if(verbose >= 1): print("\nPerforming date filtering...")
		for i in range(len(santzd_url_mat)):
			if(verbose >= 1): print("\nWorking on URL list #" + str(i+1) + "...")
			new_url_list = []
			for u in santzd_url_mat[i]:
				try:
					conn = urllib.request.urlopen(u, timeout=30)
					last_modified = conn.headers['last-modified']
					if(last_modified == None or last_modified == "None"):
						continue
					else:
						year = int(last_modified[12:16])
						if(year >= DATE_THRESHOLD):
							if(verbose >= 2): print("Source was last modified at or after 2010. Including", u)
							new_url_list.append(u)
						else:
							if(verbose >= 2): print("Source was last modified before 2010. Excluding", u)
							continue

				except:
					if(verbose >= 2): print("Failed to retrieve \'last-modified\' data. Excluding", u)
					continue
			santzd_url_mat[i] = new_url_list


	# URL matrix after filtering for last-modified date after 2010 requirement
	if(not date):
		if(verbose >= 1): print("\nSkipping date filtering...")
		santzd_url_mat = [

		]
		
	if(verbose >= 2): print(santzd_url_mat)
	if(verbose >= 1): print_url_list_lengths(santzd_url_mat)

	# –––––––––––––––––––––––––––––––––––––––––––––––––– LANG FILTERING ––––––––––––––––––––––––––––––––––––––––––––––––– #
	if(lang):
		if(verbose >= 1): print("\nPerforming language filtering...")
		for i in range(len(santzd_url_mat)):
			if(verbose >= 1): print("\nWorking on URL list #" + str(i+1) + "...")
			new_url_list = []
			for u in santzd_url_mat[i]:
				try:
					conn = urllib.request.urlopen(u, timeout=30)
					language = conn.headers['Content-language']
					if(language == None or language == "None"):
						continue
					else:
						if(language == "en"):
							if(verbose >= 2): print("Source is available in only English. Including", u)
							new_url_list.append(u)
						else:
							if(verbose >= 2): print("Source is not available in only English. Excluding", u)
							continue

				except:
					if(verbose >= 2): print("Failed to retrieve \'Content-language\' data. Excluding", u)
					continue
			santzd_url_mat[i] = new_url_list


	# URL matrix after filtering for Content-language = "en"
	if(not lang):
		if(verbose >= 1): print("\nSkipping language filtering...")
		santzd_url_mat = [

		]
		
	if(verbose >= 2): print(santzd_url_mat)
	if(verbose >= 1): print_url_list_lengths(santzd_url_mat)

	# ––––––––––––––––––––––––––––––––––––––––––––––––––– FILE OUTPUT ––––––––––––––––––––––––––––––––––––––––––––––––––– #

	idx = 1
	with open(OUTPUT_FILE, 'w') as out_file:
		print("GROUP,STRING,ALIAS,URL,COUNT", file=out_file)
		for url_lst, k in zip(santzd_url_mat, search_dict.keys()):
			for url in url_lst:
				print(str(idx) + ',' + str(queries[idx-1]) + ',' + k + ',' + url + ',' + str(len(url_lst)), file=out_file)
			idx += 1

# –––––––––––––––––––––––––––––––––––––––––––––––––––– MAIN GUARD ––––––––––––––––––––––––––––––––––––––––––––––––––– #

if __name__ == "__main__":
	main()
