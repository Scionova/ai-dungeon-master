# Tech Context: Tabletop RPG DM Agent System

## Technology Stack

| Category | Technology |
|----------|-----------|
| Language | Python 3.12+ with full type hints |
| LLM | Claude Sonnet via OpenRouter (OpenAI-compatible client) |
| Data validation | Pydantic v2 + pydantic-settings |
| CLI / display | Rich v13.9+ |
| Env config | python-dotenv |
| Dep management | Poetry (pyproject.toml + poetry.lock) |
| Testing | pytest + pytest-asyncio |
| Linting | black, ruff |

## Project Structure

```
src/rpg_dm/
├── config.py                # Config (Pydantic BaseSettings)
├── llm/
│   ├── client.py            # OpenAI-compatible client wrapper
│   └── types.py             # Message types, tool definitions
├── memory/
│   └── session_log.py       # Hierarchical event logging
├── utilities/
│   └── dice.py              # Dice rolling (full notation)
├── agents/
│   └── dm_agent.py          # DM agent with tool calling
├── game_state/
│   └── game_state.py        # Character, world state tracking
└── cli/
    └── game_cli.py          # Menu system, game loop

tests/
├── test_dice.py             # 32 tests
└── test_dm_agent.py         # 17 tests

data/sessions/               # Runtime JSON session files (not in git)
```

## Development Setup

```bash
# Install
poetry install --with dev

# Copy and fill in env
cp .env.example .env

# Run
poetry run rpg-dm

# Test
poetry run pytest
poetry run pytest --cov=src

# Lint / format
poetry run black src/ tests/
poetry run ruff check src/ tests/
```

## Environment Variables

```bash
# Required
OPENROUTER_API_KEY=sk-or-v1-...

# Optional
DM_MODEL=anthropic/claude-sonnet-4-20250514
TEMPERATURE=0.7
MAX_TOKENS=4000
DATA_DIR=data
LOG_LEVEL=INFO
```

## API Integration

```python
client = OpenAI(
    api_key=config.openrouter_api_key,
    base_url="https://openrouter.ai/api/v1"
)

response = client.chat.completions.create(
    model=config.dm_model,
    messages=messages,
    tools=tools,
    temperature=0.7,
    max_tokens=4000,
    stream=True
)
```

## Session JSON Structure

```json
{
  "session_id": "20260206_112935",
  "current_scene_id": "scene_3",
  "scenes": [
    {
      "scene_id": "scene_1",
      "title": "The Shrouded Flagon",
      "location": "A mysterious tavern",
      "participants": ["Ralph", "Guard"],
      "start_time": "2026-02-06T11:29:35.379005",
      "end_time": "2026-02-06T11:35:00.000000",
      "is_active": false,
      "summary": "Ralph enters the tavern...",
      "events": [
        {
          "timestamp": "2026-02-06T11:29:35.405088",
          "event_type": "player_action",
          "actor": "Ralph",
          "content": "I examine the door",
          "metadata": {}
        }
      ]
    }
  ]
}
```

## Known Technical Debt

1. All LLM calls are synchronous — no async support
2. No retry logic for API failures
3. No caching — every call hits the API
4. Session files grow large over time (no compression)
5. Limited error handling for API failures

## Technical Constraints

- Single player only (no concurrent session support)
- CLI only — no GUI
- Internet required for OpenRouter API
- File-based JSON persistence (no database)
