#from copy import deepcopy
import sys
from lxml import etree, html
from cssselect import GenericTranslator
from copy import deepcopy

fcontents = None
with open(sys.argv[1], encoding='utf-8') as f:
	fcontents = f.read().replace(chr(1), '\t') # work around libreoffice bug

doc = html.fromstring(fcontents)
contents = doc
head = contents[0]
body = contents[1]

moved_comments = []

for comment in head.iter(tag=[etree.Comment]):
	moved_comments.append(comment)

first_element = True
from_sheets = False
sheet_count = 0
first_moved_comment_pos = float('inf')
element_ref = None
for comment in moved_comments:
	if first_element:
		body.insert(0, comment)
		first_moved_comment_pos = 0
		first_element = False
		element_ref = comment
	else:
		element_ref.addnext(comment)
		element_ref = comment

# elements (blockquote, parent elem of comment, pos of comment)
converted_blockquotes=[]
for comment in body.iter(tag=[etree.Comment]):
	if comment.text == ' ************************************************************************** ':
		from_sheets = True
		sheet_count += 1
		continue
	elem = html.Element('blockquote')
	#print(repr(comment.text), file=sys.stderr)
	elem.text = comment.text
	elem.tail = comment.tail
	pbody = comment.getparent()
	converted_blockquotes.append((elem, pbody, pbody.index(comment)))

for elem, pbody, pbodyidx in converted_blockquotes:
	pbody[pbodyidx] = elem

for ul in body.iter(tag=['ul', 'ol']):
	for li in ul.iter('li'):
		neighbor = li.getnext()
		while neighbor is not None and neighbor.tag != 'li':
			li.append(neighbor)
			neighbor = li.getnext()

css_translator = GenericTranslator()

unique_links = set()
for link in body.xpath(css_translator.css_to_xpath('a[href]')):
	unique_links.add(link.attrib['href'])

for url in unique_links:
	elem = html.Element('a')
	elem.attrib['href'] = url
	textparts = []
	duplinks = css_translator.css_to_xpath('a[href="{}"]'.format(url))
	first_dup_link = None
	more_things = False
	for duplink in body.xpath(duplinks):
		if first_dup_link is None:
			first_dup_link = duplink
		elif not more_things:
			more_things = True
		if duplink.text is None or duplink.text.strip() == '':
			textparts.append(' ')
		else:
			textparts.append(duplink.text)
		if more_things:
			duplink.getparent().remove(duplink)
	if more_things:
		elem.text = ''.join(textparts)
		parent = first_dup_link.getparent()
		pos = parent.index(first_dup_link)
		parent[pos] = elem

multi_para_tables = []
for table in body.iter(tag=['table']):
	is_multi_para_table = False
	for td in table.iter(tag=['td']):
		first_br = True
		second_br = False
		for br in td.iter(tag=['br', 'p']):
			if first_br:
				first_br = False
			else:
				second_br = True
				break
		if second_br:
			is_multi_para_table = True
			break
	if is_multi_para_table:
		print(sys.argv[1], 'triggered multi-tables', file=sys.stderr)
		multi_para_tables.append(table)
	else:
		useless_rows = table.xpath('./tr[count(td)=1]')
		if useless_rows:
			addnextref=table
			for useless_row in useless_rows:
				useless_row_td = useless_row[0]
				useless_row_td.tag = 'p'
				table.addnext(useless_row_td)
				table.remove(useless_row)
				addnextref=useless_row_td


for table in multi_para_tables:
	check_if_useless = table.xpath('count(./tr/td)') <= 1
	table_parent = table.getparent()
	table_pos = table_parent.index(table)

	if check_if_useless:
		#transform into a bunch of paragraphs and replace the original table
		single_td = table.xpath('./tr/td[1]')[0]
		single_td.tag = 'p'
		table_parent = table.getparent()
		table_parent[table_pos] = single_td
	else:
		# number of columns
		ncols = table.xpath('count(./colgroup)')
		colnames = table.xpath('./tr[count(td)={}][1]'.format(int(ncols)))
		isel=True
		if colnames:
			colnames = colnames[0]
		else:
			isel=False
			colnames = table.xpath('./col')
			ncols = len(colnames)

		table_name_candidates = table.xpath('./tr/td[@colspan={}][1]'.format(int(ncols)))
		table_name = None
		if table_name_candidates:
			table_name = deepcopy(table_name_candidates[0])
			table_name.tag = 'h2'

		table_rep_labels = []
		table_field_guide = html.Element('ul')
		colname_count = 0
		#print(colnames, file=sys.stderr)
		for colname in colnames:
			if colname.tag == 'col':
				colname.text = "Column {}".format(colname_count)
			#copy for character sheets
			trl = deepcopy(colname)
			trl.tag = 'dt'

			#copy for field listing
			tfl = deepcopy(colname)
			tfl.tag = 'li'

			lbqs = list(trl.iter(tag=['blockquote', etree.Comment, 'br']))
			fbqs = list(tfl.iter(tag=['blockquote', etree.Comment]))
			#we don't want excessive comments or breaklines
			for bq in lbqs:
				bq.getparent().remove(bq)

			for bq in fbqs:
				# reorder comments and siblings so they appear after the content text
				sibling = bq.getnext()
				if sibling.tag not in ['blockquote', etree.Comment]:
					bq.addprevious(sibling)

			# remove random brs in field listing
			for br in tfl.iter(tag=['br']):
				br.getparent().remove(br)

			table_rep_labels.append(trl)
			table_field_guide.append(tfl)
			colname_count += 1

		if isel:
			data_row = colnames.getnext()
		else:
			data_row = colname.getnext()
		repl_rows = []
		nrow = 0
		while data_row is not None:
			table_replacement = html.Element('dl')
			for i in range(int(ncols)):
				cell = data_row[i]
				transformed_cell = deepcopy(cell)
				transformed_cell.tag = 'dd'
				cell_bqs = list(transformed_cell.iter(tag=['blockquote', etree.Comment]))
				for bq in cell_bqs:
					# reorder comments and siblings so they appear after the content text
					sibling = bq.getnext()
					if sibling.tag not in ['blockquote', etree.Comment]:
						bq.addprevious(sibling)
				# we don't want to move around the dt's!
				table_replacement.append(deepcopy(table_rep_labels[i]))
				table_replacement.append(transformed_cell)
			row_label = html.Element('h2')
			row_label.text = "Row {}".format(nrow)
			repl_rows.append(row_label)
			repl_rows.append(table_replacement)
			data_row = data_row.getnext()
			nrow+=1

		if table_name is not None:
			table_parent[table_pos] = table_name
			table_name.addnext(table_field_guide)
		else:
			table_parent[table_pos] = table_field_guide

		last_el_ref = table_field_guide
		for repl_row in repl_rows:
			last_el_ref.addnext(repl_row)
			last_el_ref = repl_row

if from_sheets:
	overview = body.xpath('./center[h1[contains(text(), "Overview")]]')
	if overview:
		top_hr=overview[0].getprevious().getprevious()
		bottom_hr=overview[0].getnext()
		body.remove(overview[0])
		body.remove(top_hr)
		body.remove(bottom_hr)

if sheet_count == 1:
	#promote lvls
	for h2 in body.iter(tag=['h2']):
		h2.tag = 'h1'
	for h3 in body.iter(tag=['h3']):
		h3.tag = 'h2'
	for h4 in body.iter(tag=['h4']):
		h4.tag = 'h3'
	for h5 in body.iter(tag=['h5']):
		h5.tag = 'h4'
	for h6 in body.iter(tag=['h6']):
		h6.tag = 'h5'

print etree.tostring(contents,pretty_print=True)
