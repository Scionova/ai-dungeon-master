# System Patterns: Tabletop RPG DM Agent System

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    CLI Interface                        │
│  (game_cli.py - Menu, Commands, Display)                │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                    DM Agent                             │
│  (dm_agent.py - LLM with Tool Calling)                  │
└─────┬──────────────┬──────────────┬─────────────────────┘
      │              │              │
┌─────▼──────┐  ┌────▼───────┐  ┌───▼──────────┐
│  Memory    │  │ Game State │  │  Utilities   │
│  System    │  │            │  │  (Dice)      │
└────────────┘  └────────────┘  └──────────────┘
```

## Core Design Patterns

### 1. Hierarchical Memory Structure

Three-level event hierarchy: `Session → Scene → Event`

```
Session (Full play session)
  ├── Scene 1 (Narrative unit)
  │   ├── Event 1 (Player action)
  │   ├── Event 2 (DM narration)
  │   └── Event 3 (Dice roll)
  └── Scene 2
      └── Events...
```

Implementation: `src/rpg_dm/memory/session_log.py`

### 2. Agent Tool Calling Pattern

DM agent autonomously calls structured tools. LLM responds with a tool call → system executes → result fed back → LLM generates narration incorporating result.

Implementation: `src/rpg_dm/agents/dm_agent.py`

### 3. Event-Driven State Updates

All state changes logged as typed events:

```python
EventType = Literal[
    "narration", "player_action", "dice_roll",
    "npc_action", "npc_dialogue", "system", "tool_call", "state_change",
]
```

### 4. Smart Context Building

Provide relevant context within token limits:
- Full events from current + N recent scenes
- Summaries for older scenes

Implementation: `src/rpg_dm/memory/session_log.py`

### 5. Command Pattern for CLI

Commands return `CommandResult` enum for type-safe flow control:

```python
class CommandResult(Enum):
    REGULAR_ACTION = "regular"
    HANDLED = "handled"
    EXIT_TO_MENU = "exit"
    QUIT_APP = "quit"
```

Implementation: `src/rpg_dm/cli/game_cli.py`

### 6. Streaming Response Pattern

LLM responses streamed chunk-by-chunk for immediate feedback and better perceived performance.

Implementation: `src/rpg_dm/agents/dm_agent.py`, `src/rpg_dm/llm/client.py`

### 7. Configuration Management

Centralized Pydantic `BaseSettings` class loads from `.env`. Single source of truth for API keys, model names, paths.

Implementation: `src/rpg_dm/config.py`

## Key Technical Decisions

| Decision | Rationale |
|----------|-----------|
| JSON session storage | Human-readable, git-friendly, no DB setup needed for MVP |
| OpenRouter for LLM | Single API for multiple models, cost-effective |
| Python + Rich for CLI | Excellent AI ecosystem, beautiful terminal output |
| Pydantic v2 for models | Type safety, JSON serialization, great error messages |
| LLM native tool calling | Reliable, structured, no regex parsing |
| Scene-based memory | Natural narrative breaks, easier to summarize |
| Poetry for deps | Deterministic builds, lock file, integrated venv |

## Data Flow: Player Action

```
CLI receives input → check if command → pass to DM Agent with session context
→ LLM processes → tool calls execute (dice, scene, etc.) → results logged
→ DM generates narrative → stream to CLI → log response → auto-save
```

## DM Agent System Prompt Structure

```
ROLE: You are the Dungeon Master for a [GENRE] campaign.

CAMPAIGN CONTEXT: setting, tone, active plot threads
CURRENT SITUATION: location, present characters, recent events, in-game time
YOUR RESPONSIBILITIES: describe world, play NPCs, enforce rules, use tools proactively
PLAYER PREFERENCES: content boundaries, challenge level, playstyle
TOOLS AVAILABLE: roll_dice, start_scene, end_scene, log_event
CURRENT SCENE: [scene_description]
```

## Patterns to Maintain

### Adding New Tools
1. Define function signature and JSON schema
2. Add to DM Agent's tool list
3. Implement execution logic with logging
4. Write tests

### Adding New Event Types
1. Add to `EventType` Literal
2. Update event logging and context building
3. Update display formatting

### Adding New Commands
1. Add to command parser, return appropriate `CommandResult`
2. Update help text and write tests

## Anti-Patterns to Avoid

- **Flat Event Log**: Always use scene hierarchy
- **Text Parsing for Tools**: Use structured tool calling
- **Manual JSON Handling**: Use Pydantic models
- **Hardcoded Paths**: Use `config.data_dir`
- **Silent Errors**: Always log and display errors
- **Blocking I/O**: Use streaming for LLM responses
- **Global State**: Pass dependencies explicitly
