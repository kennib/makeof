#!/usr/bin/env python3
from collections import defaultdict
from string import ascii_letters
from functools import reduce
import sys
import os
import random

# set the size of ngram
n = 4
# each ngram bucket is an ngram key and list of grams following that ngram
ngram_buckets = defaultdict(list)
# set the number of choices at each step of the story
num_choices = 4
# set the directory to look for books in
path = sys.argv[1] 

# split the text into grams
def split_text(raw_text):
		# separate out punctuation
		processed_text = raw_text
		for punctuation in set(raw_text) - set(ascii_letters):
			processed_text = processed_text.replace(punctuation, f' {punctuation} ')
	
		# split into grams
		grams = processed_text.split()
		
		# return the grams
		return grams


# open each book in the directory
for bookfile in os.listdir(path):
	with open(os.path.join(path, bookfile)) as book:
		# get raw text
		raw_text = book.read()

		# get the grams from the text
		grams = split_text(raw_text)
		
		# get the list of ngrams
		ngrams = zip(*[grams[i:] for i in range(n)])
		
		# put into buckets
		for *ngram, next_gram in ngrams:
			ngram_buckets[tuple(ngram)].append(next_gram)

# choose the next x grams in a story
def next_x_grams(story, x):
	# we start off with no new grams added to the story
	new_grams = []

	# until we have enough grams
	while len(new_grams) < x:
		# get the current version of the story
		current_story = story + new_grams
		# get the current story's last ngram
		ngram = current_story[-n+1:]
		# get a list of possible next grams
		next_grams = ngram_buckets.get(tuple(ngram))
		
		# if there are new possibilities
		if next_grams:
			# choose one gram
			next_gram = random.choice(next_grams)
			# add the new grams to the story
			new_grams.append(next_gram)
		# otherwise just return what we've got
		else:
			return new_grams
	
	# return the new grams 
	return new_grams
	
# format a series of grams into prose
def format_grams(grams):
	# start off with an empty string
	text = ''
	
	# start off not in a piece of quoted text
	in_quote = False

	# for every gram
	for gram in grams:
		# ...with a space in between for words and ends of sentences and starts of quotes...
		if (text and text[-1] in ascii_letters+'.,?!;:' and (gram[0] in ascii_letters or gram == '"' and not in_quote)) or (text and text[-1] == '"' and not in_quote):
			text += ' '
		# add the gram
		text += gram

		# keep track of if we're in a quote
		if gram == '"':
			in_quote = not in_quote
		
	# return the formatted text
	return text

# start a new story
story = [] 

# begin writing the story
while True:
	# if we have already started the story, choose some unique possibilities
	if story:
		choices = list(set(tuple(next_x_grams(story, n)) for choice in range(num_choices)))
	# otherwise pick a few unique random starts of sentences
	else:
		sentence_starts = [ngram for ngram in ngram_buckets.keys() if ngram[0][0].isupper()]
		choices = list(set(random.choice(sentence_starts) for choice in range(num_choices)))

	# ask for a choice
	print('Enter new words to add')
	print('or enter a "-" for each word you\'d like to remove')
	print(f'or pick an option (enter 0-{len(choices)-1}):')

	# show the choices
	for index, choice in enumerate(choices):
		print(f'({index}) {format_grams(choice)}')

	# get the choice
	selection = input()

	# if nothing was selected give new choices
	if not selection:
		continue
	# if something was selected then
	elif selection.isdigit() and int(selection) < len(choices):
		# add the choice to the story
		story += choices[int(selection)]
	# if the selection is minuses
	elif all(char == '-' for char in selection):
		story = story[:-len(selection)]
	# otherwise add the grams
	else:
		story += split_text(selection)

	# print the story
	print()
	print(format_grams(story))
	print()
