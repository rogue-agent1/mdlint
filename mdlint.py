#!/usr/bin/env python3
"""mdlint - Markdown linter."""
import argparse, re, sys, os

RULES = {
    'MD001': 'Heading levels should increment by one',
    'MD003': 'Heading style should be consistent (ATX)',
    'MD009': 'Trailing whitespace',
    'MD010': 'Hard tabs',
    'MD012': 'Multiple consecutive blank lines',
    'MD018': 'No space after # in heading',
    'MD019': 'Multiple spaces after # in heading',
    'MD022': 'Headings should be surrounded by blank lines',
    'MD023': 'Headings must start at beginning of line',
    'MD025': 'Multiple top-level headings',
    'MD032': 'Lists should be surrounded by blank lines',
    'MD041': 'First line should be a top-level heading',
    'MD047': 'File should end with single newline',
}

def lint(filepath):
    with open(filepath) as f:
        content = f.read()
    lines = content.split('\n')
    issues = []
    prev_heading = 0
    top_headings = 0
    prev_blank = True
    consecutive_blanks = 0
    
    for i, line in enumerate(lines, 1):
        # MD009: trailing whitespace
        if line.rstrip() != line and line.strip():
            issues.append((i, 'MD009', 'Trailing whitespace'))
        # MD010: hard tabs
        if '\t' in line:
            issues.append((i, 'MD010', 'Hard tab character'))
        # MD012: multiple blank lines
        if not line.strip():
            consecutive_blanks += 1
            if consecutive_blanks > 1:
                issues.append((i, 'MD012', 'Multiple consecutive blank lines'))
        else:
            consecutive_blanks = 0
        # Heading checks
        m = re.match(r'^(#{1,6})\s*(.*)', line)
        if m:
            level = len(m.group(1))
            text = m.group(2)
            # MD001
            if prev_heading and level > prev_heading + 1:
                issues.append((i, 'MD001', f'Heading jumped from h{prev_heading} to h{level}'))
            prev_heading = level
            # MD018
            if re.match(r'^#{1,6}[^ #\n]', line):
                issues.append((i, 'MD018', 'No space after # in heading'))
            # MD019
            if re.match(r'^#{1,6}  +', line):
                issues.append((i, 'MD019', 'Multiple spaces after #'))
            # MD022
            if i > 1 and lines[i-2].strip():
                issues.append((i, 'MD022', 'Heading not preceded by blank line'))
            # MD023
            if line != line.lstrip():
                issues.append((i, 'MD023', 'Heading has leading whitespace'))
            # MD025
            if level == 1:
                top_headings += 1
                if top_headings > 1:
                    issues.append((i, 'MD025', 'Multiple top-level headings'))
    
    # MD041
    if lines and not re.match(r'^# ', lines[0]):
        issues.append((1, 'MD041', 'First line should be top-level heading'))
    # MD047
    if content and not content.endswith('\n'):
        issues.append((len(lines), 'MD047', 'File should end with newline'))
    
    return issues

def main():
    p = argparse.ArgumentParser(description='Markdown linter')
    p.add_argument('files', nargs='+', help='Markdown files')
    p.add_argument('--rules', action='store_true', help='List rules')
    p.add_argument('--ignore', nargs='*', default=[], help='Rules to ignore')
    args = p.parse_args()
    
    if args.rules:
        for code, desc in sorted(RULES.items()):
            print(f"  {code}: {desc}")
        return
    
    total = 0
    for filepath in args.files:
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}"); continue
        issues = lint(filepath)
        issues = [i for i in issues if i[1] not in args.ignore]
        for line, code, msg in sorted(issues):
            print(f"  {filepath}:{line}: {code} {msg}")
        total += len(issues)
    
    if total:
        print(f"\n{total} issues found")
        sys.exit(1)
    else:
        print("No issues found ✓")

if __name__ == '__main__':
    main()
