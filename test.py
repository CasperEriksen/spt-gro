#!/usr/bin/python
# coding: utf-8

import re as re


sl = r'æ|ø|å|ß|ö|ä|ü'
w = r'\w|' + sl

text = 'huge</div><div>enormous'

text = re.sub(r'(%s|-)</div><div>(%s)' % (w, w), r'\1; \2', text)

print text

