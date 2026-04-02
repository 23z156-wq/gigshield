"""
Find the FIRST line where depth goes to 0 from 1 (potential function close) 
and trace back to find where the extra brace came from.
Show all depth changes in the range 1200-1520.
"""
import re

with open('index.html', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

inline = re.search(r'<script(?!\s+src)>([\s\S]*?)</script>', content)
assert inline
script_start = content[:inline.start(1)].count('\n') + 1
slines = inline.group(1).split('\n')

depth = 0
in_str = None
escape = False
in_line_comment = False
prev_ch = ''

with open('trace.txt', 'w', encoding='ascii', errors='replace') as out:
    for li, sline in enumerate(slines):
        html_ln = script_start + li
        old_depth = depth
        in_line_comment = False
        prev_ch = ''
        for ch in sline:
            if in_line_comment: continue
            if escape: escape = False; prev_ch = ch; continue
            if ch == '\\' and in_str: escape = True; prev_ch = ch; continue
            if in_str:
                if ch == in_str: in_str = None
                prev_ch = ch; continue
            if ch in ('"', "'", '`'): in_str = ch; prev_ch = ch; continue
            if prev_ch == '/' and ch == '/': in_line_comment = True; prev_ch = ch; continue
            if ch == '{': depth += 1
            elif ch == '}': depth -= 1
            prev_ch = ch
        
        # Show lines where depth changes in range 1190-1520
        if 1190 <= html_ln <= 1510 and old_depth != depth:
            marker = " **NEG**" if depth < 0 else ""
            out.write(f"  {html_ln}: d={old_depth}->{depth}{marker} | {sline.strip()[:110]}\n")

print("trace.txt written")
