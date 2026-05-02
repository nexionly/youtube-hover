#!/usr/bin/env python3
"""
Quick validation script for skills - standalone version without PyYAML dependency.
"""

import sys
import os
import re
from pathlib import Path

def parse_simple_yaml(yaml_text):
    """Simple parser for YAML-like frontmatter.
    
    Handles:
    - key: value
    - key: "value"
    - key: |
        multiline value
    """
    data = {}
    lines = yaml_text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith('#'):
            i += 1
            continue
            
        if ':' in line:
            key, val = line.split(':', 1)
            key = key.strip()
            val = val.strip()
            
            # Handle block scalar (multiline string)
            if val == '|':
                multiline_val = []
                i += 1
                while i < len(lines):
                    # Check if the next line is indented or empty
                    if not lines[i].strip():
                        multiline_val.append("")
                        i += 1
                    elif lines[i].startswith('  ') or lines[i].startswith('\t'):
                        multiline_val.append(lines[i][2:])
                        i += 1
                    else:
                        break
                data[key] = "\n".join(multiline_val).strip()
                continue
            
            # Handle quoted strings
            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]
            
            data[key] = val
        i += 1
    return data

def validate_skill(skill_path):
    """Basic validation of a skill."""
    skill_path = Path(skill_path)

    # Check SKILL.md exists
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return False, "SKILL.md not found"

    # Read and validate frontmatter
    content = skill_md.read_text()
    if not content.startswith('---'):
        return False, "No YAML frontmatter found"

    # Extract frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format"

    frontmatter_text = match.group(1)
    frontmatter = parse_simple_yaml(frontmatter_text)

    # Define allowed properties
    ALLOWED_PROPERTIES = {'name', 'description', 'license', 'allowed-tools', 'metadata', 'compatibility'}

    # Check for unexpected properties
    unexpected_keys = set(frontmatter.keys()) - ALLOWED_PROPERTIES
    if unexpected_keys:
        return False, (
            f"Unexpected key(s) in SKILL.md frontmatter: {', '.join(sorted(unexpected_keys))}. "
            f"Allowed properties are: {', '.join(sorted(ALLOWED_PROPERTIES))}"
        )

    # Check required fields
    if 'name' not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    if 'description' not in frontmatter:
        return False, "Missing 'description' in frontmatter"

    # Extract name for validation
    name = frontmatter.get('name', '')
    if not name:
        return False, "Empty 'name' in frontmatter"
    
    # Check naming convention (kebab-case: lowercase with hyphens)
    if not re.match(r'^[a-z0-9-]+$', name):
        return False, f"Name '{name}' should be kebab-case (lowercase letters, digits, and hyphens only)"

    # Extract and validate description
    description = frontmatter.get('description', '')
    if not description:
        return False, "Empty 'description' in frontmatter"
    
    if len(description) > 2048: # Relaxed limit for updated skill
        return False, f"Description is too long ({len(description)} characters)."

    return True, f"✅ Skill '{name}' is valid!"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python quick_validate.py <skill_directory>")
        sys.exit(1)
    
    valid, message = validate_skill(sys.argv[1])
    print(message)
    sys.exit(0 if valid else 1)