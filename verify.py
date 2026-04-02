"""
Final verification of brace balance. Output to verify.txt
"""
import re

with open('index.html', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

lines = content.split('\n')

inline = re.search(r'<script(?!\s+src)>([\s\S]*?)</script>', content)
assert inline

script = inline.group(1)
slines = script.split('\n')
script_start = content[:inline.start(1)].count('\n') + 1

depth = 0
in_str = None
escape = False
in_line_comment = False
prev_ch = ''

with open('verify.txt', 'w', encoding='ascii', errors='replace') as out:
    out.write(f"Total HTML lines: {len(lines)}\n")
    out.write(f"Script: lines {script_start}-{script_start + len(slines)}\n\n")
    
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
        
        if depth < 0:
            out.write(f"  NEGATIVE at line {html_ln}: depth={depth} | {sline.strip()[:100]}\n")
    
    out.write(f"\nFinal brace depth: {depth}\n\n")
    
    # Show the I18N area (lines 726-745)
    out.write("=== I18N area (lines 726-745) ===\n")
    for idx in range(726 - script_start, min(745 - script_start, len(slines))):
        if 0 <= idx < len(slines):
            out.write(f"  {script_start + idx}: {slines[idx][:140]}\n")
    
    # Check for encoding issues
    bad = 0
    for i, ln in enumerate(lines):
        if '\ufffd' in ln:
            bad += 1
    out.write(f"\nEncoding issues: {bad}\n")
    
    # Show last 20 lines
    out.write("\n=== Last 20 lines of script ===\n")
    for i, ln in enumerate(slines[-20:]):
        out.write(f"  {script_start + len(slines) - 20 + i}: {ln[:140]}\n")

print("verify.txt written")
