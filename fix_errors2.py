import re, sys

out = open('diag_out.txt', 'w', encoding='utf-8')

def p(*args, **kwargs):
    print(*args, **kwargs)
    print(*args, file=out, **kwargs)

with open('index.html', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

total_lines = content.count('\n')
p(f"Total lines: {total_lines}")

# Find all script tag positions
script_opens = [(m.start(), content[:m.start()].count('\n') + 1, m.group(0)) for m in re.finditer(r'<script[^>]*>', content)]
script_closes = [(m.start(), content[:m.start()].count('\n') + 1) for m in re.finditer(r'</script>', content)]

p(f"\nScript open tags: {len(script_opens)}")
for pos, line, tag in script_opens:
    p(f"  Line {line}: {tag[:80]}")

p(f"\nScript close tags: {len(script_closes)}")
for pos, line in script_closes:
    p(f"  Line {line}")

# Extract the inline <script> block (no src attribute)
inline = re.search(r'<script(?!\s+src)>([\s\S]*?)</script>', content)
if not inline:
    p("\nNo inline script block found!")
    out.close()
    sys.exit(1)

script_start_char = inline.start(1)
script_start_line = content[:script_start_char].count('\n') + 1
script_end_line = content[:inline.end()].count('\n') + 1
script = inline.group(1)
script_lines = script.split('\n')
p(f"\nInline script: HTML lines {script_start_line}-{script_end_line} ({len(script_lines)} lines of JS)")

# 1. Check for unmatched braces
depth = 0
brace_errors = []
in_str = None
escape = False
for i, ch in enumerate(script):
    if escape:
        escape = False
        continue
    if ch == '\\' and in_str:
        escape = True
        continue
    if in_str:
        if ch == in_str:
            in_str = None
        continue
    if ch in ('"', "'", '`'):
        in_str = ch
        continue
    if ch == '{':
        depth += 1
    elif ch == '}':
        depth -= 1
        if depth < 0:
            line_no = script[:i].count('\n') + script_start_line
            brace_errors.append(f"  Extra '}}' at HTML line ~{line_no}")
            depth = 0
if depth != 0:
    brace_errors.append(f"  Unmatched braces at end: net unclosed depth = {depth}")
p(f"\nBrace check: {'OK' if not brace_errors else 'ERRORS'}")
for e in brace_errors:
    p(e)

# 2. Check for unmatched parens
depth = 0
paren_errors = []
in_str = None
escape = False
for i, ch in enumerate(script):
    if escape:
        escape = False
        continue
    if ch == '\\' and in_str:
        escape = True
        continue
    if in_str:
        if ch == in_str:
            in_str = None
        continue
    if ch in ('"', "'", '`'):
        in_str = ch
        continue
    if ch == '(':
        depth += 1
    elif ch == ')':
        depth -= 1
        if depth < 0:
            line_no = script[:i].count('\n') + script_start_line
            paren_errors.append(f"  Extra ')' at HTML line ~{line_no}")
            depth = 0
if depth != 0:
    paren_errors.append(f"  Unmatched parens at end: net unclosed = {depth}")
p(f"\nParen check: {'OK' if not paren_errors else 'ERRORS'}")
for e in paren_errors:
    p(e)

# 3. Look for common JS pattern errors
p("\n--- Scanning for common issues ---")
found_issues = 0
for idx, line in enumerate(script_lines):
    abs_line = script_start_line + idx
    stripped = line.strip()
    # Double commas
    if ',,' in stripped and not stripped.startswith('//'):
        p(f"  Line {abs_line}: double comma -> {stripped[:100]}")
        found_issues += 1
    # double colon
    if '::' in stripped and not stripped.startswith('//') and 'http' not in stripped:
        p(f"  Line {abs_line}: double colon -> {stripped[:100]}")
        found_issues += 1
    # Number with colon like 1.3: true (invalid property value)
    if re.search(r'\d+\.\d+\s*:\s*(true|false)', stripped):
        p(f"  Line {abs_line}: bad numeric colon -> {stripped[:100]}")
        found_issues += 1
if found_issues == 0:
    p("  No obvious common issues found")

# 4. Show lines with replacement chars
bad_lines = []
for idx, line in enumerate(script_lines):
    if '\ufffd' in line:
        bad_lines.append((script_start_line + idx, line.strip()[:100]))
p(f"\nLines with replacement chars (encoding issues): {len(bad_lines)}")
for ln, txt in bad_lines[:30]:
    p(f"  Line {ln}: {txt}")

# 5. Show lines 700-730 to see the start of inline script
p("\n--- First 30 lines of inline script ---")
for idx, line in enumerate(script_lines[:30]):
    p(f"  {script_start_line + idx}: {line[:120]}")

# 6. Show last 30 lines of inline script
p("\n--- Last 30 lines of inline script ---")
for idx, line in enumerate(script_lines[-30:]):
    p(f"  {script_start_line + len(script_lines) - 30 + idx}: {line[:120]}")

out.close()
p("\nOutput also written to diag_out.txt")
