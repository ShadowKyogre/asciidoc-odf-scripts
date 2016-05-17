#!/bin/bash

for fname in "$@"; do
	put_here="$(dirname $(realpath "${fname}"))"
	extension="${fname##*.}"

	>&2 echo "Converting ${fname} to ${fname%%.html}.adoc"
	python2 ~/bin/odf2asciidoc/odfhtml2asciidocable.py "${put_here}/${fname}"|pandoc --from=html -t asciidoc -o "${put_here}/${fname%%.html}.adoc"
	if ! test -f "${put_here}/${fname%%.html}.adoc"; then
		continue
	fi
	if grep -q '</table>' "${put_here}/${fname}";then
		echo "would edit automagically as csheet with vim"
		vim -s "$(dirname $(realpath $0))"/chara_sheet_cmds.vim -- "${put_here}/${fname%%.html}.adoc"
	else
		echo "would edit automagically as story with vim"
		vim -s "$(dirname $(realpath $0))"/story_cmds.vim -- "${put_here}/${fname%%.html}.adoc"
	fi
done
