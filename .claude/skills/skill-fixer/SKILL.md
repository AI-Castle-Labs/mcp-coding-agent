---
name: skill-fixer
description: Diagnose and fix issues with Claude Code skills (malformed frontmatter, broken structure, loading errors, missing files). Use when a skill isn't working, won't load, or needs validation.
---

# Purpose
Use this skill to troubleshoot and repair broken or malfunctioning skills. It validates structure, fixes common issues, and ensures skills load correctly in Claude Code.

# When to Use
- Skill fails to load or isn't recognized
- User reports "skill not found" or similar errors
- Skill has syntax or formatting issues
- Need to validate a newly created skill
- Skill references broken or missing files
- User explicitly asks to "fix" or "debug" a skill

# Diagnostic Workflow

## 1. Identify the Problem
Ask or determine:
- Which skill is having issues?
- What's the error message (if any)?
- What behavior is expected vs actual?

## 2. Locate the Skill
```bash
# Find all skills
ls -la .claude/skills/

# Check specific skill structure
ls -la .claude/skills/<skill-name>/
```

## 3. Validate Structure
A valid skill must have:
- Directory: `.claude/skills/<skill-name>/`
- Main file: `SKILL.md` (required)
- Optional subdirs: `scripts/`, `references/`, `assets/`

## 4. Check SKILL.md Format

### Required Components:
```markdown
---
name: skill-name
description: Clear description of what the skill does and when to trigger it
---

# Content sections here
```

### Common Issues:
- Missing or malformed YAML frontmatter (must have `---` delimiters)
- `name` doesn't match directory name
- `description` is missing or too vague
- Invalid YAML syntax (wrong indentation, special characters)
- Extra spaces or characters before/after frontmatter

## 5. Run Validation Checks

Read the SKILL.md file and verify:
1. **Frontmatter**: Valid YAML between `---` delimiters
2. **Name field**: Present, lowercase, hyphen-separated, matches directory
3. **Description**: Present, clear, mentions when to use
4. **Content**: Has meaningful sections (# Purpose, # Usage, etc.)
5. **References**: Any linked files actually exist

## 6. Fix Common Issues

### Issue: Malformed Frontmatter
```markdown
# BAD - No delimiters
name: my-skill
description: Does something

# BAD - Wrong delimiters
***
name: my-skill
***

# GOOD
---
name: my-skill
description: Does something
---
```

### Issue: Name Mismatch
- Directory: `.claude/skills/my-cool-skill/`
- File name field: `name: my_cool_skill` ❌
- **Fix**: Change to `name: my-cool-skill` ✓

### Issue: Missing Description
```yaml
---
name: my-skill
# description missing!
---
```
**Fix**: Add clear description with trigger conditions

### Issue: Invalid Characters in YAML
```yaml
# BAD - Unquoted special chars
description: Fix: all the things & more

# GOOD - Quoted
description: "Fix: all the things & more"
```

### Issue: Broken File References
If SKILL.md references `scripts/helper.py` or `references/guide.md`:
1. Verify files exist
2. Check paths are relative to skill directory
3. Fix or remove broken references

## 7. Validation Script

Run these checks programmatically:

```python
import os
import yaml
import re

def validate_skill(skill_path):
    """Validate a skill's structure and content."""
    issues = []

    # Check SKILL.md exists
    skill_md = os.path.join(skill_path, 'SKILL.md')
    if not os.path.exists(skill_md):
        issues.append(f"Missing SKILL.md file")
        return issues

    # Read and parse
    with open(skill_md, 'r') as f:
        content = f.read()

    # Check frontmatter
    frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.match(frontmatter_pattern, content, re.DOTALL)

    if not match:
        issues.append("Missing or malformed YAML frontmatter")
        return issues

    # Parse YAML
    try:
        metadata = yaml.safe_load(match.group(1))
    except yaml.YAMLError as e:
        issues.append(f"Invalid YAML: {e}")
        return issues

    # Check required fields
    if 'name' not in metadata:
        issues.append("Missing 'name' field in frontmatter")
    elif metadata['name'] != os.path.basename(skill_path):
        issues.append(f"Name mismatch: directory='{os.path.basename(skill_path)}' vs name='{metadata['name']}'")

    if 'description' not in metadata:
        issues.append("Missing 'description' field in frontmatter")
    elif len(metadata['description']) < 20:
        issues.append("Description too short (should explain when to use)")

    # Check for content
    body = content[match.end():]
    if len(body.strip()) < 50:
        issues.append("Skill content is too short or empty")

    return issues if issues else ["✓ Skill is valid"]

# Usage
skill_dir = '.claude/skills/my-skill'
print('\n'.join(validate_skill(skill_dir)))
```

## 8. Repair Actions

Based on issues found:

1. **Fix frontmatter**: Rewrite with proper YAML syntax
2. **Rename skill**: Update directory and/or name field to match
3. **Add missing fields**: Include name and description
4. **Remove broken references**: Delete or fix file paths
5. **Improve description**: Make it clear and trigger-specific
6. **Test loading**: After fixes, verify skill loads in Claude Code

# Quick Fixes Reference

See `references/common-issues.md` for more examples and solutions.

# Testing After Fixes

1. Save all changes
2. Restart Claude Code (skills are loaded at startup)
3. Try invoking the skill with `/skill-name` or wait for auto-trigger
4. Verify skill appears in skill list (if Claude Code has that feature)

# Pro Tips

- Keep skill names short, hyphen-separated, verb-led
- Descriptions should mention specific trigger conditions
- Test skills in isolation before deploying
- Use the `mcp-structure-skill` for creating new skills properly
- Always validate YAML frontmatter before saving
- Check file permissions if skills won't load on Unix systems

# Resources
- `references/common-issues.md` — catalog of frequent skill problems and fixes
