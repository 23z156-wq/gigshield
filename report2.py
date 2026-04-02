"""
Track brace depth per line and find where depth first hits 1 and never closes.
Output to report2.txt (ASCII safe).
"""
import re

with open('index.html', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# Extract inline script
inline = re.search(r'<script(?!\s+src)>([\s\S]*?)</script>', content)
assert inline
script_start_line = content[:inline.start(1)].count('\n') + 1
script = inline.group(1)
slines = script.split('\n')

# Track depth per line
depth = 0
in_str = None
escape = False
in_line_comment = False
prev_ch = ''
line_offset = 0

depth_per_line = []  # (html_line, depth_at_end)
depth_events = []    # (html_line, char_in_line, old_depth, new_depth)
char_in_line = 0

for ci, ch in enumerate(script):
    if ch == '\n':
        depth_per_line.append((script_start_line + line_offset, depth))
        line_offset += 1
        char_in_line = 0
        in_line_comment = False
        prev_ch = ''
        continue

    char_in_line += 1

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
        old = depth
        depth += 1
        depth_events.append((script_start_line + line_offset, char_in_line, old, depth))
    elif ch == '}':
        old = depth
        depth -= 1
        depth_events.append((script_start_line + line_offset, char_in_line, old, depth))
        if depth < 0:
            depth = 0

    prev_ch = ch

with open('report2.txt', 'w', encoding='ascii', errors='replace') as out:
    out.write(f"Final brace depth: {depth}\n\n")

    # Find the LAST html line where depth was 0, and then where it rises permanently
    # Walk depth_per_line in reverse to find last line with depth=0
    last_zero_line = None
    for html_ln, d in reversed(depth_per_line):
        if d == 0:
            last_zero_line = html_ln
            break

    out.write(f"Last HTML line with depth=0: {last_zero_line}\n")
    out.write(f"(After this, depth stays > 0 until end)\n\n")

    # Show depth around the last zero line
    out.write("=== Depth per line around last-zero boundary ===\n")
    if last_zero_line:
        boundary_range = range(last_zero_line - 5, last_zero_line + 20)
        for html_ln, d in depth_per_line:
            if html_ln in boundary_range:
                js_idx = html_ln - script_start_line
                ctx = slines[js_idx].strip()[:80] if 0 <= js_idx < len(slines) else ''
                out.write(f"  Line {html_ln} depth={d}: {ctx}\n")

    # Show all depth events near the suspect lines
    out.write(f"\n=== Brace events near line {last_zero_line} ===\n")
    if last_zero_line:
        for html_ln, col, old_d, new_d in depth_events:
            if last_zero_line - 3 <= html_ln <= last_zero_line + 15:
                js_idx = html_ln - script_start_line
                ctx = slines[js_idx].strip()[:60] if 0 <= js_idx < len(slines) else ''
                brace = '{' if new_d > old_d else '}'
                out.write(f"  Line {html_ln} col {col}: '{brace}' depth {old_d}->{new_d} | {ctx}\n")

    # Show the actual lines around last_zero_line (raw content)
    out.write(f"\n=== RAW content of lines {last_zero_line} to {last_zero_line + 20} ===\n")
    if last_zero_line:
        for i in range(last_zero_line - 2, last_zero_line + 21):
            js_idx = i - script_start_line
            if 0 <= js_idx < len(slines):
                out.write(f"  {i}: {slines[js_idx][:120]}\n")

    # Also show encoding issue line (761)
    out.write(f"\n=== Line 761 raw content ===\n")
    js_idx_761 = 761 - script_start_line
    if 0 <= js_idx_761 < len(slines):
        out.write(f"  {slines[js_idx_761]}\n")
    else:
        out.write(f"  (out of range, script_start={script_start_line})\n")

print("Report2 written.")
