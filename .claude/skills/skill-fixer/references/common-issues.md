# Common Skill Issues and Fixes

## Issue 1: Skill Not Loading

### Symptoms
- Skill doesn't appear in available skills
- No error message, just silently fails

### Causes & Fixes
1. **Wrong location**: Skill must be in `.claude/skills/<name>/SKILL.md`
   - Fix: Move to correct directory structure

2. **Name mismatch**: Directory name must match `name:` field in frontmatter
   - Directory: `.claude/skills/my-skill/`
   - Frontmatter: `name: my-skill` ✓

3. **File permissions**: On Unix, file must be readable
   - Fix: `chmod 644 .claude/skills/*/SKILL.md`

4. **Claude Code not restarted**: Skills load at startup
   - Fix: Restart Claude Code

---

## Issue 2: YAML Frontmatter Errors

### Example 1: Missing Delimiters
```markdown
❌ WRONG:
name: my-skill
description: Does something

# Content...

✓ CORRECT:
---
name: my-skill
description: Does something
---

# Content...
```

### Example 2: Wrong Delimiter Characters
```markdown
❌ WRONG:
***
name: my-skill
***

❌ WRONG:
===
name: my-skill
===

✓ CORRECT:
---
name: my-skill
---
```

### Example 3: Special Characters in Description
```markdown
❌ WRONG:
description: Fix & repair skills: all types

✓ CORRECT:
description: "Fix & repair skills: all types"

✓ ALSO CORRECT:
description: Fix and repair skills for all types
```

### Example 4: Multiline Description
```markdown
❌ WRONG:
description: This skill does
  multiple things across
  several lines

✓ CORRECT:
description: >
  This skill does multiple things
  across several lines with proper
  YAML multiline syntax

✓ ALSO CORRECT (single line):
description: This skill does multiple things including X, Y, and Z
```

---

## Issue 3: Name Field Problems

### Invalid Characters
```markdown
❌ WRONG:
name: My Cool Skill    # spaces
name: my_cool_skill    # underscores
name: MyCoolSkill      # camelCase
name: skill.cool       # dots

✓ CORRECT:
name: my-cool-skill    # hyphen-separated, lowercase
```

### Name Too Long
```markdown
❌ WRONG (>64 chars):
name: my-super-amazing-incredibly-detailed-skill-that-does-everything-possible

✓ CORRECT:
name: comprehensive-skill-tool
```

---

## Issue 4: Missing or Vague Description

### Too Short
```markdown
❌ WRONG:
description: Fixes things

✓ CORRECT:
description: Diagnose and fix issues with Claude Code skills (malformed frontmatter, broken structure, loading errors). Use when a skill isn't working or needs validation.
```

### Missing Trigger Conditions
```markdown
❌ WRONG:
description: Helps with authentication tasks

✓ CORRECT:
description: Set up OAuth2 authentication flow for web apps. Use when adding social login or third-party API authentication to a project.
```

---

## Issue 5: Broken File References

### Problem
SKILL.md mentions files that don't exist:
```markdown
# Resources
- `scripts/helper.py` — does something
- `references/guide.md` — explains more
```

But files are missing.

### Fix Options
1. **Create the missing files**
2. **Remove the references** from SKILL.md
3. **Fix the paths** if files exist elsewhere

### Verification
```bash
# From skill directory
ls scripts/helper.py     # should exist
ls references/guide.md   # should exist
```

---

## Issue 6: Empty or Minimal Content

### Problem
```markdown
---
name: my-skill
description: Does something useful
---

# Usage
Use this skill.
```

### Fix
Add meaningful sections:
```markdown
---
name: my-skill
description: Does something useful when X happens
---

# Purpose
Clear explanation of what problem this solves.

# When to Use
- Specific trigger condition 1
- Specific trigger condition 2

# Workflow
1. Step one with details
2. Step two with examples
3. Step three with edge cases

# Examples
[Concrete usage examples]

# Resources
[If any scripts/references exist]
```

---

## Issue 7: Encoding Problems

### Problem
Non-ASCII characters causing parsing issues:
```markdown
---
name: my-skill
description: Cool skill with emoji 🎉 and fancy quotes ""
---
```

### Fix
Use plain ASCII or properly escape:
```markdown
---
name: my-skill
description: Cool skill with emoji (party) and standard quotes ""
---
```

---

## Issue 8: Skill Name Conflicts

### Problem
Two skills with same name in different locations.

### Fix
1. Rename one skill (both directory and name field)
2. Remove duplicate if it's outdated
3. Merge if they serve similar purposes

---

## Issue 9: Script Execution Errors

### Problem
Skill references a script that fails:
```markdown
# Usage
Run `scripts/helper.py --fix`
```

But script has syntax errors or missing dependencies.

### Fix
1. Test script independently: `python .claude/skills/my-skill/scripts/helper.py --fix`
2. Fix Python syntax errors
3. Add missing imports: `pip install required-package`
4. Update SKILL.md with correct usage or requirements

---

## Issue 10: Overly Complex Structure

### Problem
Skill has too many files, unclear organization:
```
my-skill/
  SKILL.md
  README.md
  CHANGELOG.md
  scripts/
    helper1.py
    helper2.py
    utils.py
    config.yaml
  references/
    guide1.md
    guide2.md
    notes.txt
  assets/
    image1.png
    data.json
```

### Fix
Simplify:
- Remove unnecessary README/CHANGELOG
- Combine related scripts
- Keep only essential references
- Move assets to main docs if not skill-specific

Ideal structure:
```
my-skill/
  SKILL.md           # Main skill definition
  scripts/           # Only if needed
    tool.py          # Single, well-documented script
  references/        # Only if needed
    context.md       # Single reference doc
```

---

## Quick Validation Checklist

Before declaring a skill "fixed":

- [ ] SKILL.md exists in correct location
- [ ] YAML frontmatter has proper `---` delimiters
- [ ] `name` field matches directory name
- [ ] `description` is clear and mentions triggers
- [ ] No syntax errors in YAML
- [ ] All referenced files exist
- [ ] Content is meaningful (not just placeholder text)
- [ ] Skill loads after Claude Code restart
- [ ] Skill triggers in expected scenarios
