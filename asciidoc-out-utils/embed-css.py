#!/usr/bin/env python3

from lxml.html import fromstring, tostring, Element
import sys
from os import path, environ
from urllib import request, parse as urlparse
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
			remote = False

			src_css = element.attrib['href']
			if urlparse.urlparse(src_css).scheme:
				remote = True

			if target is sys.stdin:
				if not remote:
					cssfp = path.join(environ['OTHER_SHEETS'], src_css)
				else:
					cssfp = src_css
			else:
				if not remote:
					cssfp = path.join(path.dirname(sys.argv[1]), src_css)
				else:
					cssfp = src_css


			if remote:
				with request.urlopen(cssfp) as cssf:
					cssf_contents = cssf.read().decode('utf-8')
			else:
				with open(cssfp) as cssf:
					cssf_contents = cssf.read()

			parent = element.getparent()
			element.attrib['data-href']=src_css
			del element.attrib['rel']
			del element.attrib['href']
			element.tag = 'style'
			element.text = '\n{0}'.format(cssf_contents)

	print(
		tostring(root, pretty_print=True).decode('utf-8')
	)
