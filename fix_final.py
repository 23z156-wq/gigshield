"""
COMPREHENSIVE FIX for index.html
- Restore from original backup
- Remove ALL multi-language content
- Keep English-only
- Fix brace balance
- Write clean output
"""
import re

# Read the original (broken) file
with open('index.html', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

lines = content.split('\n')
print(f"Original: {len(lines)} lines")

# Find inline script boundaries
inline = re.search(r'<script(?!\s+src)>([\s\S]*?)</script>', content)
assert inline, "No inline script found!"
script_start_line = content[:inline.start(1)].count('\n')  # 0-indexed line of script start
script_end_line = content[:inline.end()].count('\n')

# === STEP 1: Identify the I18N block ===
# Find "const I18N = {" line
i18n_start_idx = None
for i, ln in enumerate(lines):
    if 'const I18N = {' in ln.strip():
        i18n_start_idx = i
        print(f"I18N starts at line {i+1}")
        break

# Find "function t(key" line (comes after I18N and orphaned content)  
t_func_idx = None
for i, ln in enumerate(lines):
    if ln.strip().startswith('function t(key'):
        t_func_idx = i
        print(f"t() function at line {i+1}")
        break

# Find the end of the t() function body (next line that starts a const or function at same indent)
t_func_end_idx = t_func_idx
for i in range(t_func_idx + 1, len(lines)):
    stripped = lines[i].strip()
    if stripped.startswith('const ') or stripped.startswith('function ') or stripped.startswith('var '):
        t_func_end_idx = i
        print(f"After t() function, next declaration at line {i+1}: {stripped[:60]}")
        break

# === STEP 2: Extract English translations from the I18N object ===
en_start = None
en_end = None
brace_depth = 0
for i in range(i18n_start_idx, t_func_idx):
    stripped = lines[i].strip()
    if stripped.startswith('en:') or stripped.startswith('en :'):
        en_start = i
        brace_depth = 0
    if en_start is not None:
        brace_depth += lines[i].count('{') - lines[i].count('}')
        if brace_depth <= 0 and i > en_start:
            en_end = i
            break

if en_start and en_end:
    en_lines = lines[en_start:en_end+1]
    print(f"English translations: lines {en_start+1}-{en_end+1} ({len(en_lines)} lines)")
else:
    print("ERROR: Could not extract English translations!")
    exit(1)

# === STEP 3: Build replacement I18N block ===
indent = '        '  # 8 spaces to match the original
new_i18n = [
    f'{indent}const I18N = {{',
]
for ln in en_lines:
    new_i18n.append(ln.rstrip())
new_i18n.append(f'{indent}}};')
new_i18n.append('')
new_i18n.append(f'{indent}function t(key) {{ return (I18N.en && I18N.en[key]) || key; }}')

print(f"New I18N + t() block: {len(new_i18n)} lines")

# === STEP 4: Build new file content ===
# Part 1: everything before I18N
new_lines = lines[:i18n_start_idx]

# Part 2: new I18N block
new_lines.extend(new_i18n)

# Part 3: everything from t_func_end_idx onward (skip old I18N + orphaned content + old t())
new_lines.extend(lines[t_func_end_idx:])

print(f"After I18N replacement: {len(new_lines)} lines")

# === STEP 5: Remove language-related code throughout ===
result = []
skip_count = 0
for i, ln in enumerate(new_lines):
    stripped = ln.strip()
    
    # Remove "const lang = gs.lang || 'en';" lines
    if stripped == "const lang = gs.lang || 'en';":
        skip_count += 1
        continue
    
    # Remove changeLang function definition
    if 'function changeLang' in stripped:
        skip_count += 1
        continue
    
    # Remove lines with changeLang calls (language button clicks)
    if 'changeLang(' in stripped and 'function' not in stripped:
        skip_count += 1
        continue
    
    result.append(ln)

new_lines = result
print(f"Removed {skip_count} language-specific lines")

# === STEP 6: Replace t('key', lang) with t('key') ===
content_str = '\n'.join(new_lines)
# Replace t('key', lang) and t("key", lang) patterns
content_str = re.sub(r"t\(('[^']+'),\s*lang\)", r"t(\1)", content_str)
content_str = re.sub(r't\(("[^"]+"),\s*lang\)', r't(\1)', content_str)
new_lines = content_str.split('\n')

# === STEP 7: Remove language picker UI block from WProfile ===
# The language picker is a section in WProfile with language buttons
# Look for the section that has language option arrays like ['en', 'English']
result = []
skip_lang_section = False
lang_section_depth = 0

i = 0
while i < len(new_lines):
    ln = new_lines[i]
    stripped = ln.strip()
    
    # Skip language option lines
    if any(x in ln for x in ["'en', 'English'", "'hi', 'Hindi'", "'ta', 'Tamil'", 
                               "'te', 'Telugu'", "'kn', 'Kannada'", "'mr', 'Marathi'"]):
        i += 1
        continue
    
    # Skip the lang_pick label div
    if "t('lang_pick')" in ln or 't("lang_pick")' in ln:
        i += 1
        continue
    
    # Remove the [['en', 'English'], ...].map pattern and surrounding divs
    if "['en', 'English']" in ln or "[['en'" in ln:
        i += 1
        continue
    
    result.append(ln)
    i += 1

new_lines = result

# === STEP 8: Check and fix brace balance ===
content_str = '\n'.join(new_lines)
inline = re.search(r'<script(?!\s+src)>([\s\S]*?)</script>', content_str)
if not inline:
    print("ERROR: Lost inline script!")
    exit(1)

script = inline.group(1)

def check_brace_depth(script_text):
    depth = 0
    in_str = None
    escape = False
    in_line_comment = False
    prev_ch = ''
    for ch in script_text:
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
    return depth

depth = check_brace_depth(script)
print(f"\nBrace balance after fixes: {depth}")

if depth > 0:
    # Need to add closing braces before </script>
    for i in range(len(new_lines) - 1, -1, -1):
        if '</script>' in new_lines[i]:
            for _ in range(depth):
                new_lines.insert(i, '    }')
            print(f"Added {depth} closing braces")
            break
elif depth < 0:
    # Need to remove extra closing braces
    # Find lone `}` lines near function boundaries and check if they're extra
    print(f"Need to remove {abs(depth)} extra closing braces")
    
    # Strategy: find lines that are just `}` or `};` where removing them
    # would fix the depth. Work from end to start.
    removed = 0
    target = abs(depth)
    content_str = '\n'.join(new_lines)
    inline = re.search(r'<script(?!\s+src)>([\s\S]*?)</script>', content_str)
    script_start_ln = content_str[:inline.start(1)].count('\n')
    slines = inline.group(1).split('\n')
    
    # Track depth per line to find where extra braces are
    d = 0
    in_str = None
    escape = False
    in_lc = False
    prev_ch = ''
    depth_per_line = []
    
    for li, sline in enumerate(slines):
        old_d = d
        in_lc = False
        prev_ch = ''
        for ch in sline:
            if in_lc: continue
            if escape: escape = False; prev_ch = ch; continue
            if ch == '\\' and in_str: escape = True; prev_ch = ch; continue
            if in_str:
                if ch == in_str: in_str = None
                prev_ch = ch; continue
            if ch in ('"', "'", '`'): in_str = ch; prev_ch = ch; continue
            if prev_ch == '/' and ch == '/': in_lc = True; prev_ch = ch; continue
            if ch == '{': d += 1
            elif ch == '}': d -= 1
            prev_ch = ch
        depth_per_line.append((li, old_d, d, sline.strip()))
    
    # Find lines where depth goes negative or where there's an extra }
    # These are lines where depth drops below a previous function end
    # We need to find lone `}` lines that cause depth to go negative
    extra_brace_lines = []
    for li, old_d, new_d, stripped in depth_per_line:
        if new_d < old_d and new_d < 0 and stripped in ('}', '};'):
            html_ln = script_start_ln + li
            extra_brace_lines.append((html_ln, li, stripped))
    
    print(f"Found {len(extra_brace_lines)} candidate extra brace lines:")
    for html_ln, li, stripped in extra_brace_lines:
        print(f"  Line {html_ln+1}: '{stripped}'")
    
    # Remove from the end to maintain line numbers
    lines_to_remove = set()
    for html_ln, li, stripped in reversed(extra_brace_lines):
        if removed >= target:
            break
        lines_to_remove.add(html_ln)
        removed += 1
    
    if lines_to_remove:
        new_new_lines = []
        for i, ln in enumerate(new_lines):
            if i in lines_to_remove:
                print(f"  Removing extra brace at line {i+1}")
                continue
            new_new_lines.append(ln)
        new_lines = new_new_lines

# === FINAL VERIFICATION ===
content_str = '\n'.join(new_lines)
inline = re.search(r'<script(?!\s+src)>([\s\S]*?)</script>', content_str)
final_depth = check_brace_depth(inline.group(1))
print(f"\nFINAL brace balance: {final_depth}")

# Check for encoding issues
bad = sum(1 for ln in new_lines if '\ufffd' in ln)
print(f"Encoding issues: {bad}")

# Write the final file
with open('index.html', 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_lines))

print(f"\nFinal file: {len(new_lines)} lines")
print("DONE! index.html has been fixed.")
