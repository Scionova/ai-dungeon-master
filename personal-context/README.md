# Personal Context

This folder contains **your personal work-in-progress files** and is **git-ignored** to prevent merge conflicts when multiple developers work on the same repository.

## What Goes Here

### `activeContext.md` (required)
Your current work focus, recent changes, and immediate next steps. This is your personal "what am I working on right now" file that gets updated frequently as you work.

### `tasks/` folder (required)
Your personal task tracking system:
- `_index.md` - Master list of all your tasks with statuses
- `TASK###-name.md` - Individual task files with thought process, implementation plan, and progress

## Why Is This Git-Ignored?

These files change constantly as you work. If committed to git:
- ❌ Frequent merge conflicts between developers
- ❌ Noise in git history (every work session = commits)
- ❌ Privacy issues (personal notes, experiments)

With git-ignore:
- ✅ Each developer maintains their own context
- ✅ No merge conflicts
- ✅ Clean git history
- ✅ Personal workspace freedom

## What About Team Coordination?

**Shared progress tracking** happens in `memory-bank/progress.md` (committed to git):
- Update `progress.md` when you **complete** work
- Record achievements, new features, bug fixes
- This is the team's source of truth for "what's done"

**Your personal files** track ongoing work:
- Update `activeContext.md` **as you work**
- Track experiments, decisions, open questions
- This is your personal workspace

## First Time Setup

**Good news**: Files are auto-generated!

When you start working, the AI assistant will automatically:
1. Check if `activeContext.md` exists - if not, creates it from template
2. Check if `tasks/_index.md` exists - if not, creates it from template

You don't need to do anything manually. Just start working, and the AI will ensure your personal workspace is ready.

If you want to manually create them:
- Copy templates from `.github/copilot-instructions.md`
- Or just let the AI create them on your first session

- **Update often**: Keep `activeContext.md` current as you work
- **Be specific**: Detailed notes help after context switches
- **Link to code**: Reference specific files and line numbers
- **Track decisions**: Document why you chose specific approaches
- **Archive completed tasks**: Move to "Completed" section but keep the history
