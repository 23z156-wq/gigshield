"""
Analyze the full structure of index.html script to understand what needs to be removed.
Outputs to structure.txt (ASCII safe).
"""
import re

with open('index.html', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

inline = re.search(r'<script(?!\s+src)>([\s\S]*?)</script>', content)
assert inline
script_start = content[:inline.start(1)].count('\n') + 1
slines = inline.group(1).split('\n')

with open('structure.txt', 'w', encoding='ascii', errors='replace') as out:
    # Show every line that contains language-related keywords
    out.write("=== LANGUAGE / I18N / TRANSLATION REFERENCES ===\n")
    keywords = ['lang', 'LANG', 'translate', 'TRANSLATE', 'i18n', 'I18N', 'locale', 
                'LOCALE', 'hi:', 'ta:', 'te:', 'kn:', 'mr:', 'en:', 'language',
                'LANGUAGE', 'setLang', 'getLang', 'currentLang', 'langPick',
                'lang_pick', 'multilang', 'dict', 'DICT', 'T(', 't(']
    for idx, ln in enumerate(slines):
        html_ln = script_start + idx
        stripped = ln.strip()
        for kw in keywords:
            if kw in ln and not stripped.startswith('//'):
                out.write(f"  {html_ln}: {stripped[:120]}\n")
                break
    
    # Show lines 709-780 (around ZONES and where encoding issue is at 761)
    out.write("\n=== LINES 709-800 (around ZONES and encoding issue) ===\n")
    for idx in range(709 - script_start, min(800 - script_start, len(slines))):
        if 0 <= idx < len(slines):
            html_ln = script_start + idx
            out.write(f"  {html_ln}: {slines[idx][:150]}\n")

    # Show lines around where depth should be closing
    out.write("\n=== LINES 2350-2398 (end of script) ===\n")
    for idx in range(2350 - script_start, min(2399 - script_start, len(slines))):
        if 0 <= idx < len(slines):
            html_ln = script_start + idx
            out.write(f"  {html_ln}: {slines[idx][:150]}\n")

    # Find large object literals (likely the translations dict)
    out.write("\n=== LARGE OBJECT PATTERNS (const X = {) ===\n")
    for idx, ln in enumerate(slines):
        html_ln = script_start + idx
        stripped = ln.strip()
        if re.match(r'const\s+\w+\s*=\s*\{', stripped):
            out.write(f"  {html_ln}: {stripped[:120]}\n")
    
    # Find function definitions
    out.write("\n=== FUNCTION DEFINITIONS ===\n")
    for idx, ln in enumerate(slines):
        html_ln = script_start + idx
        stripped = ln.strip()
        if re.match(r'function\s+\w+', stripped) or re.match(r'const\s+\w+\s*=\s*\(', stripped) or re.match(r'const\s+\w+\s*=\s*function', stripped):
            out.write(f"  {html_ln}: {stripped[:120]}\n")

print("structure.txt written.")
