"""
Fix index.html by:
1. Replacing the broken I18N multi-language dict with English-only version
2. Removing orphaned translation content (lines ~737-~911)
3. Simplifying the t() function to English-only
4. Removing the language picker UI from WProfile
5. Fixing the 2 unclosed braces
"""
import re

with open('index.html', 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

print(f"Original file: {len(lines)} lines")

# === STEP 1: Find the I18N block boundaries ===
i18n_start = None  # line index of "const I18N = {"
t_func_start = None  # line index of "function t(key, lang)"
for i, ln in enumerate(lines):
    stripped = ln.strip()
    if 'const I18N = {' in stripped and i18n_start is None:
        i18n_start = i
        print(f"I18N starts at line {i+1}: {stripped[:60]}")
    if stripped.startswith('function t(key') and t_func_start is None:
        t_func_start = i
        print(f"t() function starts at line {i+1}: {stripped[:60]}")

# The English translations are on lines 727-736 (indices 726-735)
# Extract them from the original
en_lines = []
in_en = False
for i in range(i18n_start, t_func_start):
    stripped = lines[i].strip()
    if stripped.startswith('en:') or stripped.startswith("en :"):
        in_en = True
    if in_en:
        en_lines.append(lines[i])
        if stripped == '},':
            in_en = False
            break

print(f"\nExtracted {len(en_lines)} lines of English translations")
for ln in en_lines[:3]:
    print(f"  {ln.rstrip()[:80]}")
print("  ...")

# === STEP 2: Build the replacement for I18N block ===
# Replace lines from i18n_start through (t_func_start - 1) 
# with clean English-only I18N

new_i18n_block = []
new_i18n_block.append("        const I18N = {\n")
for ln in en_lines:
    new_i18n_block.append(ln)
new_i18n_block.append("        };\n")
new_i18n_block.append("\n")

print(f"\nNew I18N block: {len(new_i18n_block)} lines")

# === STEP 3: Build new lines array ===
new_lines = []
# Copy everything before I18N
new_lines.extend(lines[:i18n_start])
# Add new I18N block
new_lines.extend(new_i18n_block)
# Skip from i18n_start to t_func_start (the old broken I18N + orphaned content)
# Keep the t() function and everything after
new_lines.extend(lines[t_func_start:])

print(f"After I18N fix: {len(new_lines)} lines")

# === STEP 4: Remove language picker from WProfile ===
# Find the language picker section (changeLang function and language buttons)
# Look for: function changeLang and the language button grid
result_lines = []
skip_lang_picker = False
lang_buttons_depth = 0

i = 0
while i < len(new_lines):
    ln = new_lines[i]
    stripped = ln.strip()
    
    # Remove changeLang function
    if 'function changeLang' in ln:
        print(f"Removing changeLang at line {i+1}")
        i += 1
        continue
    
    # Remove language picker UI section
    # Look for the lang_pick heading and the language buttons
    if "t('lang_pick'" in ln or 't("lang_pick"' in ln:
        print(f"Removing lang_pick reference at line {i+1}: {stripped[:60]}")
        i += 1
        continue
    
    # Remove language button grid (lines with changeLang calls)
    if 'changeLang' in ln:
        print(f"Removing changeLang call at line {i+1}: {stripped[:60]}")
        i += 1
        continue
    
    # Remove the LANGUAGES constant/array if present
    if 'LANGUAGES' in ln and ('const' in ln or 'let' in ln or 'var' in ln):
        print(f"Removing LANGUAGES at line {i+1}: {stripped[:60]}")
        i += 1
        continue
    
    result_lines.append(ln)
    i += 1

new_lines = result_lines

# === STEP 5: Simplify t() function to always use English ===
# Replace: function t(key, lang) { const l = lang || 'en'; return (I18N[l] && I18N[l][key]) || (I18N['en'][key]) || key; }
# With: function t(key) { return (I18N.en && I18N.en[key]) || key; }
result_lines = []
for ln in new_lines:
    if 'function t(key, lang)' in ln:
        # Find the full function and replace
        result_lines.append("        function t(key) { return (I18N.en && I18N.en[key]) || key; }\n")
        print(f"Simplified t() function")
    else:
        result_lines.append(ln)

new_lines = result_lines

# === STEP 6: Replace t('key', lang) with t('key') throughout ===
result_lines = []
for ln in new_lines:
    # Replace patterns like t('key', lang) -> t('key')
    # and t("key", lang) -> t("key")
    modified = re.sub(r"t\(('[^']+'),\s*lang\)", r"t(\1)", ln)
    modified = re.sub(r't\(("[^"]+"),\s*lang\)', r't(\1)', modified)
    result_lines.append(modified)

new_lines = result_lines

# === STEP 7: Remove "const lang = gs.lang || 'en';" lines ===
result_lines = []
for ln in new_lines:
    stripped = ln.strip()
    if stripped == "const lang = gs.lang || 'en';":
        print(f"Removed: {stripped}")
        continue
    result_lines.append(ln)

new_lines = result_lines

# === STEP 8: Remove the language picker UI block in WProfile more thoroughly ===
# The WProfile function has a block that renders language buttons
# Let's look for the specific pattern and remove it
result_lines = []
skip_until_close = 0
for i, ln in enumerate(new_lines):
    # Skip lines that reference language selection UI elements
    if "'en', 'English'" in ln or "'hi', 'Hindi'" in ln or "'ta', 'Tamil'" in ln:
        print(f"Removing language option at line {i+1}")
        continue
    if "'te', 'Telugu'" in ln or "'kn', 'Kannada'" in ln or "'mr', 'Marathi'" in ln:
        print(f"Removing language option at line {i+1}")
        continue
    result_lines.append(ln)

new_lines = result_lines

# === STEP 9: Remove 'lang: ' from initial state if causing issues ===
# Keep lang: 'en' in state since it's harmless
# But remove any language switcher display

# === STEP 10: Verify brace balance in the script section ===
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
    
    print(f"\nBrace balance after fix: {depth} (should be 0)")
    
    if depth != 0:
        print(f"WARNING: Brace imbalance of {depth}. Attempting to fix...")
        # If depth > 0, we need to add closing braces before </script>
        # Find the </script> tag position in new_lines and add braces before it
        for i in range(len(new_lines) - 1, -1, -1):
            if '</script>' in new_lines[i]:
                # Add closing braces before this line
                fix = ""
                for _ in range(depth):
                    fix += "    }\n"
                new_lines.insert(i, fix)
                print(f"Added {depth} closing brace(s) before </script> at line {i+1}")
                break
else:
    print("WARNING: Could not find inline script to verify!")

# === WRITE OUTPUT ===
with open('index.html', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"\nFinal file: {len(new_lines)} lines")
print("index.html has been fixed!")

# === FINAL VERIFICATION ===
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

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
    print(f"\nFINAL VERIFICATION - Brace balance: {depth}")

# Check for replacement chars
bad = 0
for i, ln in enumerate(content.split('\n'), 1):
    if '\ufffd' in ln:
        bad += 1
        print(f"  Encoding issue still at line {i}: {ln.strip()[:80]}")
if bad == 0:
    print("No encoding issues found!")
