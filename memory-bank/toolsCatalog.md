# Tools Catalog

## DM Agent Tools

### Implemented ✅

| Tool | Description |
|------|-------------|
| `roll_dice` | Roll dice using standard notation (e.g. `2d6+3`, `4d6kh3`, `d20 adv`) |
| `start_scene` | Begin a new narrative scene with title and location |
| `end_scene` | Close current scene with optional summary |
| `log_event` | Record an important game event to the session log |

**Supporting (internal, not tool-callable):**
- `get_context_for_llm` — smart context with scene hierarchy
- `get_recent_context` — last N events for display
- `get_events` — query events by type, actor, scene
- `get_summary` — session statistics

### Planned (Phase 2)

**Quest & Arc Management**
- `create_quest` — define quest with objectives and rewards
- `update_quest_status` — mark progress or completion
- `get_active_quests` — list in-progress quests

**NPC Management**
- `create_npc` — generate NPC with full profile
- `update_npc` — modify NPC attributes, knowledge, goals
- `query_npc` — retrieve NPC information

**Content Generation**
- `generate_location` — create location description
- `generate_npc_on_the_fly` — quick NPC for unexpected needs
- `generate_encounter` — create combat or challenge encounter
- `generate_loot` — create treasure and rewards

## Tool Design Principles

1. **Scoped Access**: Each agent only gets tools appropriate to their role
2. **Auditable**: All tool calls logged for consistency checking
3. **Clear Errors**: Tool failures return actionable error messages
4. **Validate Input**: Check parameters before executing

## Adding New Tools

1. Define function signature and return type
2. Create JSON schema for LLM tool calling
3. Implement execution logic
4. Add event logging
5. Write tests
6. Add to this catalog

## Future Agent Types

When NPC and Orchestrator agents are implemented, they will have their own scoped tool sets. Key principle: NPCs must not have access to other NPCs' memories, player plans, or global world state beyond what their character would know.
