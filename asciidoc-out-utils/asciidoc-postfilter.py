#!/usr/bin/env python3

from lxml import html, etree
from cssselect import GenericTranslator
from os import environ
import sys

if len(sys.argv) == 1:
	target = sys.stdin
else:
	target = open(sys.argv[1], 'r', encoding='utf-8')

with target as f:
	orightml = html.parse(f).getroot()

	find_annos = GenericTranslator().css_to_xpath('a[href^="#anno-"]')
	find_anno_contents = GenericTranslator().css_to_xpath('div[id^="anno-"], .sidebar a[id^="anno-"]')

	contents = {}

	write_as_inline_comment='ADOC_HTML_INLINE' in environ

	for anno in orightml.xpath(find_anno_contents):
		if anno.tag == 'a':
			contents[anno.attrib["id"]]=anno.getparent()
			anno.getparent().attrib["class"]="{} annotation-content comment".format(anno.getparent().attrib["class"])
			anno.getparent().getparent().remove(anno.getparent())
		else:
			contents[anno.attrib["id"]]=anno
			anno.attrib["class"]="{} annotation-content comment".format(anno.attrib["class"])
			anno.getparent().remove(anno)

	for link in orightml.xpath(find_annos):
		link.tag = 'span'
		anno_id = link.attrib['href'][1:]
		del link.attrib['href']
		if anno_id in contents:
			if write_as_inline_comment:
				if contents[anno_id].text is None:
					textified = (''.join(etree.tostring(e, method='text') for e in contents[anno_id])).strip()
				else:
					textified = (contents[anno_id].text + ''.join(etree.tostring(e, method='text') for e in contents[anno_id])).strip()
				actual_comment = etree.Comment(text=textified)
				eoa_comment = etree.Comment(text="@END OF ANNOTATION@")
				actual_comment.tail = link.text
				link.text = ''
				link.insert(0, actual_comment)
				link.append(eoa_comment)
			else:
				link.attrib['class']='annotated'
				link.attrib['onclick'] = "this.parentNode.nextElementSibling.classList.toggle('visible')"
				link.addnext(contents[anno_id])

	print(etree.tostring(orightml, encoding='unicode', pretty_print=True))
