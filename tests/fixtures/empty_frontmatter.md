---
---

# Note With Empty Frontmatter

This note has frontmatter delimiters but no actual YAML content between them.

## Purpose

This tests how the script handles edge cases where:
- Frontmatter delimiters exist
- But there's no actual YAML content
- Or only whitespace between delimiters

## Expected Behavior

The script should:
1. Recognize the empty frontmatter block
2. Add the heading property
3. Maintain the frontmatter structure
4. Not break the file format

## Use Cases

This scenario might occur when:
- Users manually create frontmatter blocks
- Other tools remove frontmatter content
- Files are partially processed by other scripts

The script should handle this gracefully without errors.