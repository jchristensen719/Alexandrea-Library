# Git Commands for Workflow Changes

## Testing Changes

Before committing, ensure the Mermaid diagram renders correctly using VS Code's Markdown Preview feature.

## Using Git in Terminal

```bash
# Check status of changes
git status

# Stage the specific files we modified
git add "Alexandrea Library.code-workspace" alexandrea_workflow.md

# Commit with descriptive message
git commit -m "Fix workspace file syntax and add Alexandria Library workflow diagram"

# Push to remote repository
# Replace 'main' with your branch name if different
git push origin main
```

## Using VS Code Git Interface

```text
1. Open the Source Control panel (Ctrl+Shift+G)
2. Review changes in the "Changes" section
3. Click the "+" next to each file to stage them
4. Add a commit message in the text box
5. Click the checkmark (✓) to commit
6. Click the "..." menu and select "Push" to push your changes
```

These changes implement a comprehensive workflow diagram for the Alexandria Library project, visualizing the entire content creation, processing, and publishing lifecycle.
