# Progress: Tabletop RPG DM Agent System

**Last Updated**: February 6, 2026

## MVP Status: Complete ✅

### Implemented

| Component | File | Status |
|-----------|------|--------|
| Config management | `src/rpg_dm/config.py` | ✅ |
| LLM client (streaming + tool calling) | `src/rpg_dm/llm/` | ✅ |
| Hierarchical session log (Session→Scene→Event) | `src/rpg_dm/memory/session_log.py` | ✅ |
| Dice rolling (full notation, advantage, keep) | `src/rpg_dm/utilities/dice.py` | ✅ |
| DM agent with tool calling | `src/rpg_dm/agents/dm_agent.py` | ✅ |
| Game state (character, location, NPCs) | `src/rpg_dm/game_state/game_state.py` | ✅ |
| CLI menu + game loop + commands | `src/rpg_dm/cli/game_cli.py` | ✅ |
| Test suite (50 tests, 100% passing) | `tests/` | ✅ |

### DM Tools Available
- `roll_dice` — full notation with auto-logging
- `start_scene` — create scene with title/location
- `end_scene` — close scene with optional summary
- `log_event` — record important game events

### CLI Commands
- `/help`, `/roll <notation>`, `/state`, `/save`, `/exit`, `/quit`

## Planned (Near-term)

### High Priority
1. **Quest Tracking** — create/manage quests, link to events, track status
2. **Clock Mechanics** — progress/danger clocks for Blades in the Dark + generic use
3. **Enhanced Character Sheets** — structured stats, skills, conditions
4. **Session Search** — keyword search, filter by date/location/participants

### Medium Priority
5. **Memory Compression** — auto-generate scene summaries, compress older sessions
6. **NPC Profiles** — individual NPC memory and relationship tracking
7. **Content Generation** — location, NPC, encounter, loot generation tools

### Long-term
See [futureFeatures.md](futureFeatures.md) for full roadmap (multi-agent, web UI, multi-player, etc.)

## Known Limitations

- **Single player only** — no concurrent session support
- **No async** — all LLM calls are synchronous (blocking)
- **No caching** — every call hits the API
- **No memory compression** — session files grow large over time
- **No NPC agents** — all NPCs handled by single DM
- **No quest/faction tracking** — no formal structure yet
- **CLI only** — no GUI, voice, maps, or web interface
- **API dependency** — requires internet + OpenRouter

## Next Milestones

| Milestone | Target |
|-----------|--------|
| Enhanced Tracking (quests, clocks, character sheets, search) | 2-3 weeks |
| NPC Enhancement (profiles, memory, relationships) | 1-2 months |
| Web Interface (FastAPI + React) | 3-4 months |
| Multi-Player (PostgreSQL, Discord) | 4-6 months |
