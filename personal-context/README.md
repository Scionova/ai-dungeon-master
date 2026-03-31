# Personal Context

This folder is **git-ignored** — each developer maintains their own copy. Only `.templates/` and `README.md` are committed.

## Folder Structure

- `activeContext.md` — your current work focus, recent changes, immediate next steps
- `tasks/_index.md` — master list of all your tasks with statuses
- `tasks/TASK###-name.md` — individual task files with thought process and progress

If files are missing, copy from `.templates/`:
- `.templates/activeContext.md` → `activeContext.md`
- `.templates/tasks/_index.md` → `tasks/_index.md`
- `.templates/tasks/TASK000-template.md` → use as base for each new task file

## Personal vs Shared

| File | Audience | What goes here |
|------|----------|----------------|
| `memory-bank/progress.md` | Whole team | Completed work, achievements |
| `activeContext.md` | You only | Current focus, in-progress work |
| `tasks/` | You only | Full task history and thought process |

---

## Commands

**`add task` / `create task`** — create task file from template, document thought process, update `_index.md`.

**`update task [ID]`** — add progress log entry, update subtask statuses, sync `_index.md`.

**`show tasks [filter]`** — filters: `all`, `active`, `pending`, `completed`, `blocked`, `recent`, `tag:[name]`.

---

## Task Completion Policy

Never mark a task Completed until the user explicitly confirms it. When confirmed:

1. Move task to "Completed" in `tasks/_index.md`
2. Update `activeContext.md`
3. Update `memory-bank/progress.md` with the achievement — this is the shared team record, do not reference personal-context files here
