:let @a = "/^  +\<cr>mao--\<esc>/^\\s*__\<cr>no--\<esc>:'a,.s/^\\s\\+//\<cr>@a"
:normal @a
:%s#^\([^~]\+\)\n\([^~]\+\)\n\(\~\+\)$#\1 \2\r\3#g
:%s#\^\n\n\zs\ze[^:]\+::#[horizontal]\r#g
:%s#^_\{70\}\zs_\+\ze$##g
ZZ
