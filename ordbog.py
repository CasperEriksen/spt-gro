# coding: utf-8

import re
from collections import OrderedDict
from itertools import compress

# Angiv stierne til ordbogsfilerne nedenfor.
# Udkommenter sprog som du ikke ønsker at bruge
# EH
# -- Doubflag:
#  0 => envejs, uden reverse (storenda, stordaen, ret, frem, dansk, syn)
#  1 => envejs, med reverse
#  2 => tovejs, uden reverse (no, it, fag)
#  3 => tovejs, med reverse (en, ty, fr, sv, es)


dictionaries = OrderedDict([
	('en', {
		'name': 'Engelsk',
		'gddfile': 'data/EngelskOrdbog.gdd',
		'datfile': 'data/EngelskOrdbog.dat',
		'doubflag': 3,
	}),
	('de', {
		'name': 'Tysk',
		'gddfile': 'data/TyskOrdbog.gdd',
		'datfile': 'data/TyskOrdbog.dat',
		'doubflag': 3,
	}),
	('fr', {
		'name': 'Fransk',
		'gddfile': 'data/FranskOrdbog.gdd',
		'datfile': 'data/FranskOrdbog.dat',
		'doubflag': 3,
	}),
	#('es', {
	#	'name': 'Spansk',
	#	'gddfile': 'data/SpanskOrdbog.gdd',
	#	'datfile': 'data/SpanskOrdbog.dat',
	#	'doubflag': 3,
	#}),
	#('it',  {
	#	'name': 'Italiensk',
	#	'gddfile': 'data/ItalienskDownload.gdd',
	#	'datfile': 'data/ItalienskDownload.dat',
	#	'doubflag': 2,
	#}),
	('se',  {
		'name': 'Svensk',
		'gddfile': 'data/SvenskOrdbog.gdd',
		'datfile': 'data/SvenskOrdbog.dat',
		'doubflag': 3,
	}),
	('no',  {
		'name': 'Norsk',
		'gddfile': 'data/NorskDownload.gdd',
		'datfile': 'data/NorskDownload.dat',
		'doubflag': 2,
	}),
	('enfag', {
		'name': 'Engelsk (Fag/Teknik)',
		'gddfile': 'data/FagordbogEngelskDownload.gdd',
		'datfile': 'data/FagordbogEngelskDownload.dat',
		'doubflag': 2,
	}),
	('daen', {
		'name': 'Stor Dansk-Engelsk',
		'gddfile': 'data/StorDanskEngelskDownload.gdd',
		'datfile': 'data/StorDanskEngelskDownload.dat',
		'doubflag': 0,
	}),
	('enda', {
		'name': 'Stor Engelsk-Dansk',
		'gddfile': 'data/StorEngelskDanskDownload.gdd',
		'datfile': 'data/StorEngelskDanskDownload.dat',
		'doubflag': 0,
	}),
	#	('ret', {
	#		'name': 'Retskrivning',
	#		'gddfile': 'data/RetskrivningsordbogDownload.gdd',
	#		'datfile': 'data/RetskrivningsordbogDownload.dat',
	#		'doubflag': 0,
	#	}),
	#	('frem', {
	#		'name': 'Fremmedord',
	#		'gddfile': 'data/DanskFremmedordbogDownload.gdd',
	#		'datfile': 'data/DanskFremmedordbogDownload.dat',
	#		'doubflag': 0,
	#	}),
	('da', {
		'name': 'Dansk',
		'gddfile': 'data/DanskDownload.gdd',
		'datfile': 'data/DanskDownload.dat',
		'doubflag': 0,
	}),
	#	('syn', {
	#		'name': 'Synonymer',
	#		'gddfile': 'data/SynonymordbogDownload.gdd',
	#		'datfile': 'data/SynonymordbogDownload.dat',
	#		'doubflag': 0,
	#	}),
])


class BColour:
	end, default = 0, 39
	bold, dim, italic, underlined = 1, 2, 3, 4
	red, green, yellow, blue = 31, 32, 33, 34
	magenta, cyan, lgray = 35, 36, 37
	lred, lgreen, lyellow, lblue = 91, 92, 93, 94
	lmagenta, lcyan = 95, 96


class Colour:
	# custom dictionary colours
	italic = [BColour.italic]
	bold = [BColour.bold]
	header1 = [BColour.lblue, BColour.bold, BColour.underlined] # Dansk-[sprog] / [sprog]-Dansk
	header2 = [30, 1, 107] # Opslagsord, ordforbindelser og 'reverse' resultater
	term = [BColour.blue]
	fx = [BColour.dim, BColour.magenta]
	examples = [BColour.lgray]
	se = [BColour.dim, BColour.magenta]
	wordclass = [BColour.dim]
	error1 = [BColour.red]
	error2 = [BColour.red, BColour.bold]
	gray = [BColour.lgray]
	inbrackets = [BColour.dim]
	info = [BColour.dim, BColour.green, BColour.italic]
	end = [BColour.end]


def ans(c):
	return '\033[' + str(c[0]) + 'm'


def ansi(s, c):
	if not c:
		return s
	elif len(c) == 1:
		return ansi_(s, c[0])
	else:
		return ansi(ansi_(s, c[0]), c[1:])


def ansi_(s, c): return '\033[' + str(c) + 'm' + s + '\033[0m'


def li(x, y, indentwidth, indent):
	space = ' ' * indentwidth * indent
	if len(y) == 0:
		y = ['LINE INDENT ERROR (this message is only for testing)']
	return {
		'ol':  str(y[-1]) + '. ' + space,
		'ola': space + str(y[-1]) + '. ', #chr(y + 96)
		'ul': space + u'\u2022 '.encode('utf8')
	}.get(x, '')


def entry_to_text(entry, language, dtype):
	sl = r'æ|Æ|ø|Ø|å|Å|ß|ö|Ö|ä|Ä|ü|Ü'
	S = r'\S|' + sl
	w = r'\w|' + sl
	b = r'[\s<>\\/_]'

	text = re.sub(r'<a href="expand://(.+?)">\[INFO\]', ansi(r'(\1)', Colour.info), entry)
	text = re.sub(r'<a href="sound.+?>\[LYD\]', '', text)
	text = re.sub(r'<a href="lookup.+?>', '', text)
	text = re.sub(r'<a href="search.+?>', '', text)

	# Colour the header
	if re.search('<h2>(.+?)</h2>', text):
		text = re.sub(r'<h3>.*?</h3>', '', text)
		text = re.sub(r'<h2>(.+?)<', ansi(r'\1', Colour.term)+'<', text)
	else:
		text = re.sub('<h3>(.+)</h3>', ansi(r'\1 ', Colour.term), text)

	# Colour other things
	text = text.replace(r'<font color="#888888">', ans(Colour.gray))
	text = text.replace(r'<font color="#605A50">', ans(Colour.wordclass))
	text = text.replace(r'fx</font>', 'fx')
	text = re.sub(r'</font>', ans(Colour.end), text)
	text = re.sub(r'<span><font color="purple">fx(.+?)</span>', ansi('fx', Colour.fx)+ansi(r'\1', Colour.examples), text)

	text = text.replace(r'<i>', ans(Colour.italic))
	text = text.replace(r'</i>', ans(Colour.end))
	text = re.sub(r'(%s)se også(%s)' % (b, b), r'\1' + ansi(r'se også', Colour.se) + r'\2', text)
	text = re.sub(r'(%s)se\b' % b, r'\1' + ansi(r'se', Colour.se), text)

	# If en dictionary, colour the pronunciation
	if language == 'en':
		text = re.sub(r'</h2><div>(\[.+?\])\s*', ansi(r'\1', Colour.gray)+' ', text)
	if language == 'en' and dtype == 'collocation_lookup':
		text = text.lstrip('<div></div>')
		text = re.sub(r'^\[.+?\] </a></div>', '', text)

	# Remove <div> elements, taking care to appropriately add or remove spacing
	text = re.sub(r'</h2><div>\s*', '', text)
	text = re.sub(r'(%s|-)</div><div>(%s)' % (w, w), r'\1; \2', text)
	text = text.replace(r'</div></div><div>', ' ')
	text = text.replace(r'<div></div>', ' ')
	text = text.replace(r'</div><div>', ' ')

	# Remove specified elements
	redundancies = [r'</h2>',r'<span>', r'</span>', r'<div>', r'</div>', r'</a>', r' [LYD]', r'<p2>', r'</p1>']
	for s in redundancies:
		text = text.replace(s, '')

	# Remove obvious double/trible spaces
	text = re.sub(r'(%s)\s{2,3}(%s)' % (S, S), r'\1 \2', text)

	# Remove leading spaces
	text = text.lstrip()

	indentwidth = 4
	indent = -1
	output = ""
	i = 0
	j = []
	l = []
	while i < len(text):
		s = r = ''
		if text[i:].startswith(r'<ol>'):
			l.append('ol')
			j.append(0)
			indent += 1
			i += 4
		elif text[i:].startswith(r'<ul>'):
			l.append('ul')
			indent += 1
			i += 4
		elif text[i:].startswith(r'<ol type="a">'):
			l.append('ola')
			j.append(0)
			indent += 1
			i += 13
		elif text[i:].startswith(r'</ol>'):
			l.pop()
			j.pop()
			indent -= 1
			i += 5
		elif text[i:].startswith(r'</ul>'):
			l.pop()
			indent -= 1
			i += 5
		elif text[i:].startswith(r'<li>'):
			if l[-1] is not 'ul':
				j[-1] += 1
			output += '\n'
			output += li(l[-1], j, indentwidth, indent)
			i += 4
		elif text[i:].startswith(r'</li>'):
			i += 5
		else:
			output += text[i]
			i += 1

	if language == 'enda':
		output = output.replace('(vi.) ', '')
		output = output.replace('(vt.) ', '')
		output = output.replace('vi., ', '')
	if language == 'de':
		output = output.replace(' <int.>', '')
		output = output.replace('<sub>', ' (')
		output = output.replace('</sub>', ')')
	if language == 'es':
		output = output.replace('¡ ', '!')
	output = output.replace('&lt;', ans(Colour.gray)+'<')
	output = output.replace('&gt;', '>'+ans(Colour.end))
	output = output.replace(' ?', '?')
	output = output.replace(' !', '!')
	output = re.sub(r'(\(.+?\))', ansi(r'\1', Colour.inbrackets), output)
	output = output.rstrip(' ')
	return output


def relevance_sort(search_results, search_term):
	not_top = [True for _ in search_results]
	for idx, text in enumerate(search_results):
		res = re.search(str(Colour.term[0])+r'm(.+?)\\', repr(text))
		if res and res.group(1).startswith(search_term):
			not_top[idx] = False
	if all(not_top): return search_results
	return [x for (_, x) in sorted(zip(not_top, search_results))]


def print_results(search_results, search_terms, directions, tables, language):
	search_term = " ".join(search_terms)


	text_results = []
	for d, d_name in directions:
		text_results.append([ansi(d_name, Colour.header1)])
		tid = 1
		for t, t_name in tables:
			if t == "reverse":
				res = re.search('(\w+)-(\w+)', d_name)
				t_name += ' fra ' + res.group(2) + '-' + res.group(1)
			else:
				t_name += ' fra ' + d_name
			text_results.append([ansi(t_name, Colour.header2)])
			entries = search_results[d][t]
			for idx, entry in enumerate(entries):
				text = entry_to_text(entry, language, t)
				if text:
					text_results[tid].append(text + "\n")
			if len(text_results[tid]) > 1:
				text_results[tid][0] = '\n' + text_results[tid][0] + '\n'
			tid += 1

	no_results = []
	for idx, lst in enumerate(text_results):
		if idx > 0:
			if len(lst) > 1:
				no_results.append(False)
				if lst[0] == '\n'+ansi('Opslagsord', Colour.header2):
					text_results[idx][1:-1] = relevance_sort(text_results[idx][1:-1], search_term)
			else:
				no_results.append(True)

	text_results = list(compress(text_results, [False] + [not x for x in no_results]))

	if True:
		if all(no_results):
			ordbog = directions[0][1]
			if len(directions) > 1:
				ordbog += "-Dansk"
			print ansi(ansi("Ingen resultater", Colour.bold), Colour.error1)
			print ansi("'%s'" % search_term,Colour.error2)+ansi(" findes ikke som opslagsord i ", Colour.error1)+ansi(ordbog, Colour.error2)
		else:
			for text_list in text_results:
				for text in text_list:
					print text
