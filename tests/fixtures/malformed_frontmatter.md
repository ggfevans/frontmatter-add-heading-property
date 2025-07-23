---
title: Malformed Frontmatter Example
author: Test Author
tags: [test, malformed
description: This YAML has syntax errors
invalid: yaml: structure: here
missing_quote: this should be "quoted"
unclosed_bracket: [item1, item2
nested:
  proper: value
  malformed: [unclosed
---

# Malformed Frontmatter Test

This file contains intentionally malformed YAML frontmatter to test error handling.

The frontmatter above has several syntax errors:
- Unclosed brackets in tags array
- Invalid colon usage
- Missing quotes where needed
- Unclosed nested array

The script should handle this gracefully and either:
1. Skip the file with a warning
2. Parse what it can and ignore invalid parts
3. Treat the file as having no frontmatter

## Expected Behavior

When processing this file, the script should:
- Detect the malformed YAML
- Log an appropriate warning
- Continue processing other files
- Not crash or throw unhandled exceptions