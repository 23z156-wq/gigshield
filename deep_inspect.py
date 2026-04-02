"""
Deep inspector for index.html:
- Finds the inline <script> block
- Reports ALL brace/paren mismatches WITH context
- Reports encoding issues
- Reports first/last N lines of the script for context
"""
import re, json

with open('index.html', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

lines = content.split('\n')
print(f"Total HTML lines: {len(lines)}")

# Find all script tags
for i, ln in enumerate(lines, 1):
    if '<script' in ln or '</script>' in ln:
        print(f"  HTML line {i}: {ln.strip()[:80]}")

# Extract inline script block
inline = re.search(r'<script(?!\s+src)>([\s\S]*?)</script>', content)
if not inline:
    print("ERROR: No inline script found")
    exit(1)

script_start_line = content[:inline.start(1)].count('\n') + 1
script = inline.group(1)
slines = script.split('\n')
print(f"\nInline script starts at HTML line {script_start_line}, total JS lines: {len(slines)}")

# --- Brace depth tracking, recording deepest/shallowest ---
depth = 0
in_str = None
escape = False
in_comment = False
prev_ch = ''
brace_history = []  # (char_offset, html_line, depth)
depth_by_line = {}  # html_line -> depth at end of line

char_offset = 0
line_offset = 0
for ch in script:
    if ch == '\n':
        depth_by_line[script_start_line + line_offset] = depth
        line_offset += 1
    if not in_comment:
        if escape:
            escape = False
        elif ch == '\\' and in_str:
            escape = True
        elif in_str:
            if ch == in_str:
                in_str = None
        elif ch in ('"', "'", '`'):
            in_str = ch
        elif prev_ch == '/' and ch == '/':
            in_comment = 'line'
        elif ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth < 0:
                html_ln = script_start_line + line_offset
                print(f"  EXTRA }} at HTML line {html_ln}: {slines[line_offset].strip()[:80]}")
                depth = 0
    elif in_comment == 'line' and ch == '\n':
        in_comment = False

    prev_ch = ch
    char_offset += 1

print(f"\nFinal brace depth at end of script: {depth} (should be 0)")

# Find lines where depth changes dramatically (suspected problem areas)
print("\n--- Lines where depth deviates (depth < 0 or sudden spikes) ---")
prev_d = 0
for ln_no in sorted(depth_by_line.keys()):
    d = depth_by_line[ln_no]
    if abs(d - prev_d) > 3:
        js_idx = ln_no - script_start_line
        ctx = slines[js_idx].strip()[:100] if 0 <= js_idx < len(slines) else ''
        print(f"  Line {ln_no}: depth {prev_d} -> {d}: {ctx}")
    prev_d = d

# Show lines with replacement chars
print("\n--- Lines with encoding replacement chars ---")
found = 0
for idx, ln in enumerate(slines):
    if '\ufffd' in ln:
        html_ln = script_start_line + idx
        print(f"  HTML line {html_ln}: {ln.strip()[:100]}")
        found += 1
print(f"Total: {found}")

# Show first 10 lines of script
print(f"\n--- FIRST 15 lines of script (starting HTML line {script_start_line}) ---")
for i, ln in enumerate(slines[:15]):
    print(f"  {script_start_line + i:4d}: {ln[:120]}")

# Show last 15 lines of script
print(f"\n--- LAST 15 lines of script ---")
for i, ln in enumerate(slines[-15:]):
    print(f"  {script_start_line + len(slines) - 15 + i:4d}: {ln[:120]}")

# Scan for common bad patterns
print("\n--- Pattern scan ---")
patterns = [
    (r',,', "double comma"),
    (r':\s*true\s*,\s*\w+\s*:\s*\d+\.\d+\s*:', "mixed bool/float property"),
    (r"'\s*\+\s*'[^']*'\s*\+\s*'", "check concat"),
    (r'}\s*}\s*}\s*}\s*}', "many closing braces"),
]
for idx, ln in enumerate(slines):
    html_ln = script_start_line + idx
    for pat, label in patterns:
        if re.search(pat, ln):
            print(f"  Line {html_ln} [{label}]: {ln.strip()[:100]}")

print("\nComplete.")
