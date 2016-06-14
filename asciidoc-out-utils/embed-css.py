#!/usr/bin/env python3

from lxml.html import fromstring, tostring, Element
import sys
from os import path, environ
import re

if len(sys.argv) == 1:
	target = sys.stdin
else:
	target = open(sys.argv[1], 'r', encoding='utf-8')

with target  as f:
	f_contents = f.read()
	root = fromstring(f_contents)

	for element in root.iter('link'):
		if element.attrib['rel'] == 'stylesheet' and element.attrib['type'] == 'text/css':
			if target is sys.stdin:
				cssfp = path.join(environ['OTHER_SHEETS'], element.attrib['href'])
			else:
				cssfp = path.join(path.dirname(sys.argv[1]), element.attrib['href'])

			with open(cssfp) as cssf:
				cssf_contents = cssf.read()

			parent = element.getparent()
			element.attrib['data-href']=element.attrib['href']
			del element.attrib['rel']
			del element.attrib['href']
			element.tag = 'style'
			element.text = '\n{0}'.format(cssf_contents)

	print(
		tostring(root, pretty_print=True).decode('utf-8')
	)
