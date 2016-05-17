:%s/\n\n +\n\n/\r +\r +\r/g
:%s/\(_\+\)\n +\n +/\1\r\r/g
:%s/\(?\{2,\}\)/$$\1$$/g
:%s/ +\nChapter/ +\r\rChapter/g
:%s/ +\nSection/ +\r\rSection/g
:%s/ +\n +\n\* / +\r +\r\r* /g
:%s/^\(Chapter\)\([^~]\+\)\n\([^~]\+\)/\1\2 \3/g
:%s#^_\{70\}\zs_\+\ze$##g
ZZ
