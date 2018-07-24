#!/usr/bin/python
# coding: utf-8

import argparse, sys
from ordbog import dictionaries


def write(s):
	sys.stdout.write(str(s))


def helper():
	description = u'Helper function for extracting data from DICTIONARIES'
	parser = argparse.ArgumentParser(description=description)
	parser.add_argument('--dict', action='store_true')
	parser.add_argument('--name', nargs='?')#, choices=dictionaries.keys())
	parser.add_argument('--doubflag', nargs='?')#, choices=dictionaries.keys())
	args = parser.parse_args()

	arg = [(x, y) for (x, y) in vars(args).iteritems() if y]
	if len(arg) is not 1:
		sys.exit('Invalid number of arguments in "helper.py": received %d, expected 1' % len(arg))

	(key, val) = arg[0]

	if key == "name" or key == "doubflag":
		if val in dictionaries:
			print dictionaries[val][key]
	elif key == "dict":
		print " ".join(dictionaries.keys())


if __name__ == '__main__':
	helper()
