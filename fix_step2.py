"""
Remove the 3 leftover lines from the old t() function (lines 740-742).
Then re-verify brace balance.
"""
import re

with open('index.html', 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

print(f"Before fix: {len(lines)} lines")

# Lines to remove (0-indexed: 739, 740, 741)
# Line 740: "const l = lang || 'en';"
# Line 741: "return (I18N[l] && I18N[l][key]) || (I18N['en'][key]) || key;"
# Line 742: "}"

# Find and remove these specific lines
new_lines = []
removed = 0
for i, ln in enumerate(lines):
    line_num = i + 1
    stripped = ln.strip()
    # Remove the old t() function body remnants
    if stripped == "const l = lang || 'en';" and 738 <= line_num <= 742:
        print(f"Removing line {line_num}: {stripped}")
        removed += 1
        continue
    if stripped == "return (I18N[l] && I18N[l][key]) || (I18N['en'][key]) || key;" and 738 <= line_num <= 743:
        print(f"Removing line {line_num}: {stripped}")
        removed += 1
        continue
    if stripped == '}' and 738 <= line_num <= 744 and removed == 2:
        print(f"Removing line {line_num}: {stripped}")
        removed += 1
        continue
    new_lines.append(ln)

print(f"Removed {removed} lines")

# Also need to remove the 3 extra closing braces that fix_all.py added before </script>
# Check the end of the file for those
for i in range(len(new_lines) - 1, max(0, len(new_lines) - 20), -1):
    stripped = new_lines[i].strip()
    if stripped == '}' and i > 0:
        next_stripped = new_lines[i+1].strip() if i+1 < len(new_lines) else ''
        # Check if this is one of the extra braces added near </script>
        # Look for pattern: multiple } lines right before </script>
        pass

# Write fixed file
with open('index.html', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"After fix: {len(new_lines)} lines")

# Verify brace balance
content = ''.join(new_lines)
inline = re.search(r'<script(?!\s+src)>([\s\S]*?)</script>', content)
if inline:
    script = inline.group(1)
    depth = 0
    in_str = None
    escape = False
    in_line_comment = False
    prev_ch = ''
    for ch in script:
        if ch == '\n':
            in_line_comment = False
            prev_ch = ''
            continue
        if in_line_comment:
            prev_ch = ch
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
    print(f"\nFinal brace balance: {depth} (should be 0)")
else:
    print("ERROR: Could not find inline script!")
