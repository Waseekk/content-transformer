# Git Workflow Guidelines

## Branch Strategy

### Branch Structure
```
master (production)
├── streamlit-cloud (deployment fixes, version 1)
├── base-model (current workflow backup)
└── swiftor (active development for version 2. production ready version)
```

**All branches merge directly to master**

### Branch Purposes

| Branch | Purpose | Merge Target |
|--------|---------|--------------|
| `master` | Production  app - stable release | - |
| `streamlit-cloud` | Streamlit Cloud deployment optimizations | `master` |
| `base-model` | Saves current workflow with enhancement options | `master` |
| `swiftor` | Active development for next version (Swiftor app) | `master` |

---

## Commit Message Standards

### Format
```
type: concise description in lowercase

Optional body with more details if needed.
```

### Commit Types

- **feat**: new feature or functionality
- **fix**: bug fix or error correction
- **refactor**: code restructuring without behavior change
- **docs**: documentation updates
- **test**: test additions or modifications
- **chore**: maintenance tasks (deps, config, etc.)
- **perf**: performance improvements
- **style**: code formatting, whitespace, etc.

### Examples

✅ **Good Commits:**
```
feat: add user authentication endpoints
fix: resolve token expiration issue in JWT middleware
refactor: extract scraper logic into service layer
docs: update API documentation for translation endpoints
test: add unit tests for enhancement service
chore: update dependencies to latest versions
perf: optimize database queries with indexing
```

❌ **Bad Commits:**
```
Update files 🚀
Fixed stuff
changes
WIP - still working on this
feat: add amazing feature! 🤖
Updated code with AI assistance
```

### Rules

1. **No emojis** - Keep it professional
2. **No AI mentions** - Don't reference Claude, GPT, or any AI tools
3. **Lowercase descriptions** - Consistent formatting
4. **Concise but descriptive** - Balance brevity and clarity
5. **Present tense** - "add feature" not "added feature"
6. **Imperative mood** - "fix bug" not "fixes bug"

---

## Workflow Process

### Starting a New Session

When you start a new chat, say:
```
check git
```

Claude will:
1. Show current branch
2. Display recent commits
3. Show uncommitted changes
4. Suggest next steps based on context

### Working on Features

**Active development:**
- Use `swiftor` branch for all new feature work and cloud work
- Merges directly to `master` when ready

**Saving current state:**
- Use `base-model` to snapshot current workflow
- Think of it as a backup of working code

**Deployment fixes:**
- dont use Use `streamlit-cloud' branch for any changes until user ask. it has version 1
- Merges to `master` after testing

### Making Commits

When ready to commit, ask:
```
commit these changes
```

Claude will:
1. Review changed files with `git status` and `git diff`
2. Draft a formal commit message following conventions
3. Show you the message for approval
4. Execute the commit

### Branch Operations

| Task | Say this |
|------|----------|
| Check context | "check git" |
| Switch branch | "switch to swiftor" |
| See changes | "show me what changed" |
| Commit work | "commit these changes" |
| Create branch | "create branch [name]" |

---

## Context Preservation

### What Claude Reads at Session Start

1. **`.claude/branches.json`** - Branch metadata and purposes
2. **`git branch --show-current`** - Active branch
3. **`git log -10 --oneline`** - Recent commit history
4. **`git status --short`** - Current uncommitted changes

This allows seamless continuity across chat sessions - Claude knows exactly where you left off.

---

## Quick Reference

### Typical Workflow

```bash
# Start new session
You: "check git"
Claude: [Shows current branch, recent commits, changes]

# Work on feature
You: [Make changes to code]

# Commit when ready
You: "commit these changes"
Claude: [Reviews changes, suggests commit message]
You: "yes, commit it"
Claude: [Executes formal commit]
```

### Branch Usage

- **Daily work** → `swiftor`
- **Save current state** → `base-model`
- **Deployment fixes** → `swiftor`
- **Production** → `master` (protected)

---

**Last Updated:** 2026-01-01
