"""
Write ALL diagnostic info to sections in a plain ASCII file.
"""
import re, sys

OUTFILE = 'report.txt'

with open('index.html', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

lines = content.split('\n')
slines_total = len(lines)

# Find inline <script> block
inline = re.search(r'<script(?!\s+src)>([\s\S]*?)</script>', content)
assert inline, "No inline script found!"

script_start_line = content[:inline.start(1)].count('\n') + 1
script = inline.group(1)
slines = script.split('\n')

with open(OUTFILE, 'w', encoding='ascii', errors='replace') as out:
    out.write(f"=== REPORT ===\n")
    out.write(f"Total HTML lines: {slines_total}\n")
    out.write(f"Script starts at HTML line: {script_start_line}\n")
    out.write(f"Script ends at HTML line: {script_start_line + len(slines) - 1}\n")
    out.write(f"Total JS lines: {len(slines)}\n\n")

    # Script tag positions
    out.write("=== SCRIPT TAGS ===\n")
    for i, ln in enumerate(lines, 1):
        if '<script' in ln or '</script>' in ln:
            out.write(f"  HTML line {i}: {ln.strip()[:80]}\n")

    # Brace depth tracking per line
    depth = 0
    in_str = None
    escape = False
    in_line_comment = False
    prev_ch = ''
    line_offset = 0
    depth_at_end_of_line = []
    line_issues = []

    for ci, ch in enumerate(script):
        if ch == '\n':
            depth_at_end_of_line.append((script_start_line + line_offset, depth))
            line_offset += 1
            in_line_comment = False
            continue

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
            if depth < 0:
                html_ln = script_start_line + line_offset
                ctx = slines[line_offset].strip()[:80] if line_offset < len(slines) else ''
                line_issues.append(f"  EXTRA_BRACE at HTML line {html_ln}: {ctx}")
                depth = 0

        prev_ch = ch

    out.write(f"\n=== BRACE DEPTH FINAL: {depth} (should be 0) ===\n")

    out.write("\n=== BRACE ISSUES ===\n")
    if line_issues:
        for issue in line_issues:
            out.write(issue + "\n")
    else:
        out.write("  None\n")

    out.write("\n=== DEPTH ANOMALIES (change > 3 in one line) ===\n")
    prev_d = 0
    for html_ln, d in depth_at_end_of_line:
        if abs(d - prev_d) > 3:
            js_idx = html_ln - script_start_line
            ctx = slines[js_idx].strip()[:100] if 0 <= js_idx < len(slines) else ''
            out.write(f"  Line {html_ln}: {prev_d} -> {d}: {ctx}\n")
        prev_d = d

    out.write("\n=== ENCODING ISSUES (replacement chars) ===\n")
    ec = 0
    for idx, ln in enumerate(slines):
        if '\ufffd' in ln:
            html_ln = script_start_line + idx
            out.write(f"  HTML line {html_ln}: {ln.strip()[:100]}\n")
            ec += 1
    out.write(f"Total encoding issues: {ec}\n")

    out.write("\n=== FIRST 20 LINES OF SCRIPT ===\n")
    for i, ln in enumerate(slines[:20]):
        out.write(f"  {script_start_line + i:4d}: {ln[:120]}\n")

    out.write("\n=== LAST 20 LINES OF SCRIPT ===\n")
    for i, ln in enumerate(slines[-20:]):
        out.write(f"  {script_start_line + len(slines) - 20 + i:4d}: {ln[:120]}\n")

    out.write("\n=== PATTERN SCAN ===\n")
    patterns = [
        (r',,', "double_comma"),
        (r'}\s*}\s*}\s*}\s*}', "5+_closing_braces"),
    ]
    found = 0
    for idx, ln in enumerate(slines):
        html_ln = script_start_line + idx
        for pat, label in patterns:
            if re.search(pat, ln) and not ln.strip().startswith('//'):
                out.write(f"  Line {html_ln} [{label}]: {ln.strip()[:100]}\n")
                found += 1
    if found == 0:
        out.write("  None found\n")

print("Report written to report.txt")
