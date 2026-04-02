"""
Run report on the CURRENT index.html to see what it looks like after fix_all.py
"""
import re

with open('index.html', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

lines = content.split('\n')

inline = re.search(r'<script(?!\s+src)>([\s\S]*?)</script>', content)
assert inline
script_start = content[:inline.start(1)].count('\n') + 1
slines = inline.group(1).split('\n')

with open('report3.txt', 'w', encoding='ascii', errors='replace') as out:
    out.write(f"Total lines: {len(lines)}\n")
    out.write(f"Script: lines {script_start}-{script_start + len(slines)}\n\n")
    
    # Show lines 726-780 (I18N area)
    out.write("=== LINES 720-810 (I18N area) ===\n")
    for idx in range(720 - script_start, min(810 - script_start, len(slines))):
        if 0 <= idx < len(slines):
            html_ln = script_start + idx
            out.write(f"  {html_ln}: {slines[idx][:140]}\n")
    
    # Track brace depth line by line in the I18N area
    out.write("\n=== BRACE DEPTH per line (720-810) ===\n")
    depth = 0
    in_str = None
    escape = False
    in_line_comment = False
    prev_ch = ''
    for li, sline in enumerate(slines):
        html_ln = script_start + li
        old_depth = depth
        in_line_comment = False
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
        
        if 720 <= html_ln <= 810:
            if old_depth != depth:
                out.write(f"  {html_ln}: depth {old_depth}->{depth} | {sline.strip()[:100]}\n")
    
    out.write(f"\nFinal depth at end of script: {depth}\n")

print("report3.txt written")
