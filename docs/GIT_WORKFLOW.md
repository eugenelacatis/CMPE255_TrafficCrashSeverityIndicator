# Git Workflow

Rules for how we use Git on this project.

## The Golden Rule

**Never push directly to `main`.**

All changes go through pull requests.

## Branch Naming

Use this format: `name/description`

Examples:
- `eugene/webapp-setup`
- `alex/time-features`
- `jordan/baseline-model`
- `sam/eda-notebook`

Keep descriptions short (2-4 words, lowercase, hyphens).

## Workflow

### Starting New Work

```bash
# Make sure you're on main and up to date
git checkout main
git pull origin main

# Create your branch
git checkout -b yourname/feature-description
```

### While Working

Commit often. Small commits are better than big ones.

```bash
git add .
git commit -m "Add weather feature encoding"
```

Push your branch regularly (at least daily when actively working):

```bash
git push origin yourname/feature-description
```

### When Done

1. Push your final changes
2. Go to GitHub and create a Pull Request
3. Fill out the PR template
4. Request a review (anyone on the team)
5. After approval, merge it yourself

### Staying Updated

If `main` has changed while you were working:

```bash
git checkout main
git pull origin main
git checkout yourname/feature-description
git merge main
# Fix any conflicts, then push
git push origin yourname/feature-description
```

## Pull Requests

### Who Approves?

Anyone on the team can approve. Just need 1 approval to merge.

### What to Check in a Review

- Does the code run without errors?
- Are notebooks cleared of output before committing?
- Is there a brief description of what changed?
- No API keys or secrets committed?

### Merging

Use "Squash and merge" to keep history clean.

After merging, you can delete your branch on GitHub.

## Commit Messages

Keep them short and descriptive:

**Good:**
- `Add time-based features`
- `Fix null handling in weather column`
- `Update EDA notebook with correlation plot`

**Bad:**
- `updates`
- `fixed stuff`
- `WIP`

## What NOT to Commit

These are in `.gitignore` but double-check:

- `.env` files with secrets
- `__pycache__/` folders
- `.ipynb_checkpoints/`
- Large files over 50MB
- Personally identifiable data

## Common Commands Reference

```bash
# See current status
git status

# See what branch you're on
git branch

# Switch branches
git checkout branch-name

# See recent commits
git log --oneline -10

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Discard local changes to a file
git checkout -- filename

# See what's different
git diff
```

## Help, I Messed Up

### "I committed to main by accident"

If you haven't pushed yet:
```bash
git reset --soft HEAD~1
git checkout -b yourname/fix-description
git add .
git commit -m "Your message"
git push origin yourname/fix-description
```

If you already pushed, tell the team in Discord and we'll fix it together.

### "I have merge conflicts"

1. Open the conflicting files
2. Look for `<<<<<<<`, `=======`, `>>>>>>>` markers
3. Edit to keep the code you want
4. Remove the markers
5. `git add .` and `git commit`

Ask for help if stuck.

### "I need to undo a pushed commit"

Don't force push. Create a new commit that reverts:
```bash
git revert <commit-hash>
git push
```
