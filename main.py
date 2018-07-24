#!/usr/bin/python
# coding: utf-8

import os
import sys
import dictionary
import argparse
from ordbog import print_results, dictionaries


# Python 2.7
if sys.version_info[0] != 2 or sys.version_info[1] < 7:
	sys.exit('This program requires Python2.7+')


def is_empty(search_results):
	# Function to check if search_results are empty
	return not any([any(d.values()) for d in search_results.values()])


def main():
	# check om sprogene er tilgængelige
	filenotfound = False
	for d in dictionaries.keys():
		lang = dictionaries[d]
		if not (os.path.exists(lang['gddfile']) and os.path.exists(lang['datfile'])):
			print 'Ordbogsfiler for %s kan ikke findes i mappen %s' % (
				lang['name'], os.path.dirname(os.path.abspath(lang['gddfile'])))
			filenotfound = True
	if filenotfound:
		return
	dic = dictionary.Dictionary(dictionaries)

	description = u'Blå og brugervenlig ordbog'
	parser = argparse.ArgumentParser(description=description)
	parser.add_argument('search_terms', nargs="+")
	parser.add_argument('-l', '--lang', nargs='?',
						default='en', dest='lang', choices=dictionaries.keys(),
						help=u'language (enda, daen, de, fr)')
	parser.add_argument('-p', '--path', nargs='?', default='./',
						dest='path', help='path til data filer (.dat and .gdd)')
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

	tables = [('lookup', 'Opslagsord'), ('collocation_lookup', 'Ordforbindelser')]
	if dictionaries[language]['doubflag'] == 1  or dictionaries[language]['doubflag'] == 3:
		tables.append(('reverse', 'Resultater'))


	search_results = dic.lookup(search_terms, language)
	print_results(search_results, search_terms, directions, tables, language)


if __name__ == '__main__':
	main()
