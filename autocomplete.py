#!/bin/usr/python
# coding: utf-8

import re
from ordbog import dictionaries
from itertools import compress
import dictionary
import os
import argparse


def relevance_sort(search_results, search_term):
	not_top = [not bool(re.match(search_term, text)) for text in search_results]
	return [x for (_, x) in sorted(zip(not_top, search_results))]


def find_recommendations(dic, search_terms, directions, tables, language):
	n = sum([len(term) for term in search_terms])
	search_terms[-1] += "%"
	search_results = dic.lookup(search_terms, language)
	search_terms[-1] = search_terms[-1][:-1]

	matches = ['000']
	for d, d_name in directions:
		for t, t_name in tables:
			entries = search_results[d][t]
			for entry in entries:
				term = re.search(r'<h2>(.+?)<', entry)
				if not term: term = re.search(r'<h3>(.+?)<', entry)
				if term:
					term = term.group(1).rstrip()
					if term != matches[-1]:
						matches.append(term)
	return matches[1:]


def tab(dic, search_terms, directions, tables, language):
	matches = find_recommendations(dic, search_terms, directions, tables, language)

	search_term = " ".join(search_terms)
	fil = [m.startswith(search_term) for m in matches]
	if len(fil) < 2 or all(fil):
		commonprefix = os.path.commonprefix(matches)
	else:
		commonprefix = os.path.commonprefix(list(compress(matches, fil)))
		fil2 = [not f for f in fil]
		matches = [m for (_, m) in sorted(zip(fil2, matches))]

	return commonprefix, matches


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('search_terms', nargs="+")
	parser.add_argument('-l', '--lang', nargs='?',
						default='en', dest='lang', choices=dictionaries.keys(),
						help=u'language (enda, daen, de, fr)')
	parser.add_argument('-t', '--trans', nargs='?', default=0, dest="translate",
						choices=['0', '1', '2'], help='0: from Danish, 1: to Danish, 2: both ways')
	args = parser.parse_args()

	translate = int(args.translate)
	language = args.lang
	search_terms = [term.lstrip(' ').rstrip(' ') for term in args.search_terms]
	language_name = dictionaries[language]['name']
	directions = [('fromDanish', 'Dansk-%s' % language_name), ('toDanish', '%s-Dansk' % language_name)]
	if dictionaries[language]['doubflag'] < 2 or translate == 0:
		del directions[1]
	elif translate == 1:
		del directions[0]

	dic = dictionary.Dictionary(dictionaries)
	tables = [('lookup', 'Artikler')]
	if len(search_terms) > 1:
		tables.append(('collocation_lookup', 'Ordforbindelser'))
	prefix, tab_terms = tab(dic, search_terms, directions, tables, language)

	if not tab_terms and len(search_terms) == 1:
		tables = [('collocation_lookup', 'Ordforbindelser')]
		prefix, tab_terms = tab(dic, search_terms, directions, tables, language)

	ofile = open('tabterms.txt', 'w')
	ofile.write("%s\n" % " ".join(search_terms))
	ofile.write("%s\n" % prefix)
	if len(tab_terms) >= 1:
		for term in tab_terms:
			ofile.write("%s\n" % (term))
	else:
		ofile.write("")
	ofile.close()


if __name__ == '__main__':
	main()
