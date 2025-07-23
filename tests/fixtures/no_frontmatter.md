# Note Without Frontmatter

This is a simple markdown note that doesn't have any YAML frontmatter.

## Purpose

This file is used to test the script's behavior when processing files that don't have frontmatter blocks.

## Expected Behavior

When processing this file, the script should:
1. Detect that there's no existing frontmatter
2. Generate an appropriate heading value based on the filename
3. Add a new frontmatter block at the beginning
4. Preserve all existing content

## Content Structure

The note contains:
- A main heading
- Multiple sections
- Standard markdown formatting
- No existing YAML frontmatter

## Links and References

- [[Related Note]]
- [[Another Note Without Frontmatter]]

This tests the script's ability to handle files in their "natural" state before any frontmatter processing.