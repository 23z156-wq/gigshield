"""
Show lines 1390-1520 with brace depth tracking to find the root cause.
"""
import re

with open('index.html', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

inline = re.search(r'<script(?!\s+src)>([\s\S]*?)</script>', content)
assert inline
script_start = content[:inline.start(1)].count('\n') + 1
slines = inline.group(1).split('\n')

# Track depth up to the problem area
depth = 0
in_str = None
escape = False
in_line_comment = False
prev_ch = ''

with open('problem_area.txt', 'w', encoding='ascii', errors='replace') as out:
    for li, sline in enumerate(slines):
        html_ln = script_start + li
        old_depth = depth
        in_line_comment = False
        prev_ch = ''
        for ch in sline:
            if in_line_comment:
                continue
            if escape:
                escape = False
                prev_ch = ch
                continue
            if ch == '\\' and in_str:
                escape = True
                prev_ch = ch
                continue
            if in_str:
                if ch == in_str:
                    in_str = None
                prev_ch = ch
                continue
            if ch in ('"', "'", '`'):
                in_str = ch
                prev_ch = ch
                continue
            if prev_ch == '/' and ch == '/':
                in_line_comment = True
                prev_ch = ch
                continue
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
            prev_ch = ch
        
        # Show all lines in the problem range with depth info
        if 1390 <= html_ln <= 1520:
            marker = " **NEG**" if depth < 0 else ""
            change = f" [{old_depth}->{depth}]" if old_depth != depth else ""
            out.write(f"  {html_ln} d={depth}{change}{marker}: {sline.rstrip()[:120]}\n")

print("problem_area.txt written")
