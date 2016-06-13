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
				with open(path.join(environ['OTHER_SHEETS'], element.attrib['href'])) as cssf:
					cssf_contents = cssf.read()
					inlined = Element('style', {'type': 'text/css'})
					inlined.text = cssf_contents
			else:
				with open(path.join(path.dirname(sys.argv[1]), element.attrib['href'])) as cssf:
					cssf_contents = cssf.read()
					inlined = Element('style', {'type': 'text/css'})
					inlined.text = cssf_contents

			parent = element.getparent()
			parent.remove(element)
			parent.append(inlined)

	print(
		tostring(root, pretty_print=True).decode('utf-8')
	)
