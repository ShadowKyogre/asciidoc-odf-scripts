#!/usr/bin/env python3

from pynliner import Pynliner
# from lxml.html.soupparser import fromstring
from lxml.html import fromstring, tostring
import sys
from os import path, environ
import re

with open(sys.argv[1], 'r', encoding='utf-8') as f:
	#f_contents = f.read().replace('\r', '')
	f_contents = f.read()
	inliner = Pynliner()
	root = fromstring(f_contents)

	for element in root.iter('link'):
		if element.attrib['rel'] == 'stylesheet' and element.attrib['type'] == 'text/css':
			with open(path.join(path.dirname(sys.argv[1]), element.attrib['href'])) as cssf:
				cssf_contents = cssf.read()
				inliner.with_cssString(cssf_contents)
			element.getparent().remove(element)
	
	for element in root.iter('div'):
		if 'class' in element.attrib and element.attrib['class'] == 'section':
			del element.attrib['class']
	
	if 'ADOC_PYNLINE_COLORS' in environ:
		inliner.with_cssString("body { color: none; }\n")
	else:
		inliner.with_cssString("body {color: black; background: white;}")

	print(inliner.from_string(tostring(root, pretty_print=True, encoding='unicode')).run())
