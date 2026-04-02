import re, sys

with open('index.html', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

total_lines = content.count('\n')
print(f"Total lines: {total_lines}")

# Find all <script> and </script> positions
script_opens = [(m.start(), content[:m.start()].count('\n') + 1) for m in re.finditer(r'<script[^>]*>', content)]
script_closes = [(m.start(), content[:m.start()].count('\n') + 1) for m in re.finditer(r'</script>', content)]

print(f"\nScript open tags: {len(script_opens)}")
for pos, line in script_opens:
    print(f"  Line {line}: {content[pos:pos+60].strip()}")

print(f"\nScript close tags: {len(script_closes)}")
for pos, line in script_closes:
    print(f"  Line {line}: {content[pos:pos+20].strip()}")

# Extract the inline <script> block (no src attribute)
inline = re.search(r'<script(?!\s+src)>([\s\S]*?)</script>', content)
if not inline:
    print("\nNo inline script block found!")
    sys.exit(1)

script_start_line = content[:inline.start()].count('\n') + 1
script_end_line = content[:inline.end()].count('\n') + 1
script = inline.group(1)
script_lines = script.split('\n')
print(f"\nInline script: lines {script_start_line}–{script_end_line} ({len(script_lines)} lines)")

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
            brace_errors.append(f"  Extra '}}' at script line ~{line_no}")
            depth = 0
if depth != 0:
    brace_errors.append(f"  Unmatched braces at end: net depth = {depth}")
print(f"\nBrace check: {'OK' if not brace_errors else 'ERRORS'}")
for e in brace_errors:
    print(e)

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
            paren_errors.append(f"  Extra ')' at script line ~{line_no}")
            depth = 0
if depth != 0:
    paren_errors.append(f"  Unmatched parens at end: net depth = {depth}")
print(f"\nParen check: {'OK' if not paren_errors else 'ERRORS'}")
for e in paren_errors:
    print(e)

# 3. Look for common JS pattern errors
print("\n--- Scanning for common issues ---")
for idx, line in enumerate(script_lines):
    abs_line = script_start_line + idx
    stripped = line.strip()
    # Double commas
    if ',,' in stripped and not stripped.startswith('//'):
        print(f"  Line {abs_line}: double comma -> {stripped[:80]}")
    # Trailing comma before }
    if re.search(r',\s*\}', stripped) and not stripped.startswith('//'):
        pass  # valid in modern JS, skip
    # colon colon
    if '::' in stripped and not stripped.startswith('//') and '//' not in stripped[:stripped.find('::')]:
        print(f"  Line {abs_line}: double colon -> {stripped[:80]}")
    # Missing comma between properties (key: val key: val)
    if re.search(r"'\s*\n?\s*[a-zA-Z_]+\s*:", line) and not stripped.startswith('//'):
        pass  # not easily detectable here

# 4. Show lines with replace chars
bad_lines = []
for idx, line in enumerate(script_lines):
    if '\ufffd' in line:
        bad_lines.append((script_start_line + idx, line.strip()[:80]))
print(f"\nLines with replacement chars (encoding issues): {len(bad_lines)}")
for ln, txt in bad_lines[:20]:
    print(f"  Line {ln}: {txt}")

print("\nDone.")
