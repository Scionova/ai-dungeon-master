---
applyTo: '**'
---
Coding standards, domain knowledge, and preferences that AI should follow.

# Tabletop RPG DM Agent System - Project Instructions

## Memory Bank Location

**Shared Team Context** (committed to git) — all files in `memory-bank/`:

| File | Purpose |
|------|---------|
| [projectbrief.md](../memory-bank/projectbrief.md) | Project vision and scope |
| [productContext.md](../memory-bank/productContext.md) | User needs and experience goals |
| [systemPatterns.md](../memory-bank/systemPatterns.md) | Architecture patterns and data flows |
| [techContext.md](../memory-bank/techContext.md) | Technology stack and setup |
| [progress.md](../memory-bank/progress.md) | Implementation status and completed work |
| [toolsCatalog.md](../memory-bank/toolsCatalog.md) | Complete tools catalog by agent type |
| [futureFeatures.md](../memory-bank/futureFeatures.md) | Roadmap, phases, open questions |

**Personal Context** (git-ignored, per developer) — all files in `personal-context/`:

| File | Purpose |
|------|---------|
| `activeContext.md` | Your current work focus |
| `tasks/` | Your task tracking with `_index.md` |

If personal-context files are missing, copy from `personal-context/.templates/`. See [README.md](../personal-context/README.md) for task management details.

## Important Project Rules

1. **Session files in `data/sessions/`** — auto-generated, don't edit manually
2. **Always reference Memory Bank files first** before making changes
3. **Update `progress.md`** after completing work (shared team visibility)
4. **Update `activeContext.md`** as you work (personal, git-ignored)
5. **Create task files in `personal-context/tasks/`** for your work
6. **Update README.md when installation/usage changes**

## Memory Bank Structure

Files build on each other in a clear hierarchy:

```
projectbrief.md
├── productContext.md
├── systemPatterns.md
└── techContext.md
         └── progress.md
                  └── activeContext.md  (personal)
                           └── tasks/   (personal)
```

### Core Files

1. `projectbrief.md` — Foundation document, source of truth for project scope
2. `productContext.md` — Why this project exists, problems it solves, UX goals
3. `progress.md` — What works, what's left, current status, known issues
4. `systemPatterns.md` — Architecture, key technical decisions, design patterns
5. `techContext.md` — Technologies, dev setup, constraints, dependencies

## Documentation Updates

Update Memory Bank when:
- Discovering new project patterns
- After implementing significant changes
- When prompted with **update memory bank** (review ALL files)
- When context needs clarification

What to capture:
- Critical implementation paths
- User preferences and workflow
- Project-specific patterns
- Known challenges and decisions
- Tool usage patterns
