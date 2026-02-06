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

**Pattern**: Three-level event hierarchy provides natural organization

```
Session (Full play session)
  ├── Scene 1 (Narrative unit)
  │   ├── Event 1 (Player action)
  │   ├── Event 2 (DM narration)
  │   └── Event 3 (Dice roll)
  ├── Scene 2
  │   └── Events...
  └── Scene 3
      └── Events...
```

**Benefits**:
- Natural narrative breaks
- Efficient context building (full recent scenes, older summaries)
- Easy to query and filter
- Human-readable structure

**Implementation**: `src/rpg_dm/memory/session_log.py`

### 2. Agent Tool Calling Pattern

**Pattern**: DM agent autonomously calls structured tools

```python
# DM decides action needs dice roll
tools = [
    {
        "type": "function",
        "function": {
            "name": "roll_dice",
            "description": "Roll dice using standard notation",
            "parameters": {
                "notation": {"type": "string"},
                "reason": {"type": "string"}
            }
        }
    }
]

# LLM responds with tool call
# System executes tool
# Result fed back to LLM
# LLM generates narration incorporating result
```

**Benefits**:
- DM acts autonomously
- Structured, reliable tool execution
- Clear audit trail
- Extensible (easy to add new tools)

**Implementation**: `src/rpg_dm/agents/dm_agent.py`

### 3. Event-Driven State Updates

**Pattern**: All state changes logged as events

```python
# Event types
EventType = Literal[
    "narration",      # DM descriptive text
    "player_action",  # Player input
    "dice_roll",      # Tool: roll outcome
    "npc_action",     # NPC behavior
    "npc_dialogue",   # NPC speech
    "system",         # System messages
    "tool_call",      # Tool execution
    "state_change",   # Game state update
]

# Every action creates an event
session_log.log_event(
    event_type="dice_roll",
    actor="DM",
    content=f"Rolled {result}",
    metadata={"notation": "d20", "total": 15}
)
```

**Benefits**:
- Complete audit trail
- Easy to replay/debug
- Supports undo/rollback (future)
- Enables analytics

**Implementation**: `src/rpg_dm/memory/session_log.py`

### 4. Smart Context Building

**Pattern**: Provide relevant context within token limits

```python
def build_context(recent_scenes=2):
    context = []

    # Full events from current scene
    context += current_scene.events

    # Full events from N recent scenes
    for scene in recent_scenes[-N:]:
        context += scene.events

    # Summaries from older scenes
    for scene in older_scenes:
        context += scene.summary

    return context
```

**Benefits**:
- Stay within token limits
- Prioritize recent, relevant information
- Maintain long-term continuity
- Efficient token usage

**Implementation**: `src/rpg_dm/memory/session_log.py`

### 5. Command Pattern for CLI

**Pattern**: Commands return enum for flow control

```python
class CommandResult(Enum):
    REGULAR_ACTION = "regular"    # Normal player input
    HANDLED = "handled"            # Command processed
    EXIT_TO_MENU = "exit"          # Return to main menu
    QUIT_APP = "quit"              # Shut down

def handle_command(user_input: str) -> tuple[CommandResult, str]:
    if user_input.startswith("/exit"):
        return CommandResult.EXIT_TO_MENU, ""
    elif user_input.startswith("/quit"):
        return CommandResult.QUIT_APP, ""
    # ... other commands
    else:
        return CommandResult.REGULAR_ACTION, user_input
```

**Benefits**:
- Type-safe flow control
- Clear command vs action distinction
- Easy to add new commands
- Predictable behavior

**Implementation**: `src/rpg_dm/cli/game_cli.py`

### 6. Streaming Response Pattern

**Pattern**: Stream LLM responses for better UX

```python
# Streaming narration
for chunk in dm_agent.respond_streaming(player_action):
    print(chunk, end="", flush=True)
print()  # Newline after complete response
```

**Benefits**:
- Immediate feedback
- Creates suspense
- Better perceived performance
- Handles long responses well

**Implementation**: `src/rpg_dm/agents/dm_agent.py`, `src/rpg_dm/llm/client.py`

### 7. Configuration Management

**Pattern**: Centralized, validated configuration

```python
class Config(BaseSettings):
    # API settings
    openrouter_api_key: str
    dm_model: str = "anthropic/claude-sonnet-4-20250514"

    # Paths
    data_dir: Path = Path("data")

    # Validation
    @field_validator("openrouter_api_key")
    def validate_api_key(cls, v):
        if not v or v == "your_api_key_here":
            raise ValueError("Invalid API key")
        return v

# Load from .env automatically
config = Config()
```

**Benefits**:
- Single source of truth
- Type safety and validation
- Environment variable support
- Easy to test with different configs

**Implementation**: `src/rpg_dm/config.py`

## Key Technical Decisions

### 1. JSON for Session Persistence

**Decision**: Use JSON files for session storage

**Rationale**:
- Human-readable for debugging
- Git-friendly (can track changes)
- No database setup required
- Easy to backup and share
- Sufficient for MVP single-player use

**Trade-offs**:
- ❌ Not suitable for multi-player
- ❌ No query optimization
- ✅ Simple, reliable, portable

**Future**: Migrate to database for multi-player

### 2. OpenRouter for LLM Access

**Decision**: Use OpenRouter API (OpenAI-compatible)

**Rationale**:
- Access to multiple models (Claude, GPT, etc.)
- Single API for different providers
- Good rate limits and reliability
- Cost-effective

**Trade-offs**:
- ❌ Requires internet connection
- ❌ API costs
- ✅ No model hosting required
- ✅ Access to best models

**Future**: Add local model support (Ollama)

### 3. Python with Rich for CLI

**Decision**: Python + Rich library for terminal UI

**Rationale**:
- Python has excellent AI/ML ecosystem
- Rich provides beautiful terminal output
- Rapid development
- Cross-platform (though MVP is Linux)

**Trade-offs**:
- ❌ Terminal-only (no GUI)
- ❌ CLI less accessible for some users
- ✅ Fast to build and iterate
- ✅ Professional appearance

**Future**: Web UI with React/Next.js

### 4. Pydantic for Data Validation

**Decision**: Use Pydantic v2 for all data models

**Rationale**:
- Type safety with runtime validation
- Excellent IDE support
- JSON serialization built-in
- Great error messages

**Implementation**:
- Config settings
- LLM message types
- Game state models
- Roll results

### 5. Tool Calling via LLM

**Decision**: Use LLM's native tool calling instead of text parsing

**Rationale**:
- Reliable, structured execution
- No regex or parsing needed
- Clear separation of concerns
- Easy to add new tools

**Implementation**:
- Define tools as JSON schemas
- LLM responds with tool calls
- System executes and returns results
- LLM generates final response

### 6. Scene-Based Memory

**Decision**: Organize events into scenes rather than flat log

**Rationale**:
- Natural narrative breaks
- Easier to summarize and compress
- Better context relevance
- Matches how humans think about stories

**Implementation**:
- Scenes have title, location, participants
- Auto-started or manually triggered
- Can be ended with summary

### 7. Poetry for Dependency Management

**Decision**: Use Poetry instead of pip + requirements.txt

**Rationale**:
- Deterministic builds
- Better dependency resolution
- Integrated virtual environment
- Publishing support

**Trade-offs**:
- ❌ Extra tool to learn
- ✅ Reliable, professional workflow
- ✅ Lock file for reproducibility

## Component Relationships

### Data Flow: Player Action

```
1. CLI receives player input
   ↓
2. Check if command (/roll, /exit, etc.)
   ↓ (if regular action)
3. Pass to DM Agent with session context
   ↓
4. DM Agent processes with LLM
   ↓ (may call tools)
5. Tools execute (dice roll, scene start, etc.)
   ↓
6. Results logged as events
   ↓
7. DM generates narrative response
   ↓
8. Stream response to CLI
   ↓
9. Response logged as event
   ↓
10. Auto-save session
```

### Data Flow: Session Load

```
1. CLI shows session list
   ↓
2. User selects session
   ↓
3. SessionLog loads JSON file
   ↓
4. Parse sessions → scenes → events
   ↓
5. Build recent context for display
   ↓
6. Show last N events to player
   ↓
7. Ready for next player action
```

## Testing Strategy

### Unit Tests
- **Dice Rolling**: 32 tests covering all notations
- **DM Agent**: 17 tests for tool calling, streaming
- **Session Log**: Event logging, scene management
- **Game State**: State updates, queries

### Integration Tests (Future)
- End-to-end gameplay flow
- Session save/load cycle
- Multi-turn conversations
- Command handling

### Test Fixtures
```python
@pytest.fixture
def config():
    return Config(openrouter_api_key="test_key")

@pytest.fixture
def session_log(tmp_path):
    return SessionLog(session_id="test", data_dir=tmp_path)

@pytest.fixture
def dm_agent(config, session_log):
    return DMAgent(config, session_log)
```

## Patterns to Maintain

### Adding New Tools
1. Define function signature
2. Create JSON schema for tool definition
3. Add to DM Agent's tool list
4. Implement tool execution logic
5. Add logging for tool usage
6. Write tests

### Adding New Event Types
1. Add to EventType Literal
2. Update event logging
3. Add to context building logic
4. Update display formatting
5. Document in architecture

### Adding New Commands
1. Add to command parser
2. Return appropriate CommandResult
3. Update help text
4. Handle state changes
5. Write tests

## Anti-Patterns to Avoid

❌ **Flat Event Log**: Always use scene hierarchy
❌ **Text Parsing for Tools**: Use structured tool calling
❌ **Manual JSON Handling**: Use Pydantic models
❌ **Hardcoded Paths**: Use config.data_dir
❌ **Silent Errors**: Always log and display errors
❌ **Blocking I/O**: Use streaming for LLM responses
❌ **Global State**: Pass dependencies explicitly

## Data Flow Examples

Understanding how data flows through the system helps maintain architectural integrity.

### Example 1: Player Takes Action

```
1. Player: "I persuade the guard to let us through"
   ↓
2. CLI receives input
   ↓
3. Check if command (/roll, /exit, etc.)
   ↓ (regular action)
4. Pass to DM Agent with session context
   ↓
5. DM Agent processes with LLM
   ↓
6. DM decides: needs dice roll
   ↓
7. Tool Call: roll_dice(notation="1d20+3", reason="Persuasion check")
   ↓
8. Dice utility executes roll
   ↓
9. Result: RollResult(total=15, rolls=[12], modifier=3)
   ↓
10. Log event: dice_roll with metadata
   ↓
11. LLM generates outcome based on roll
   ↓
12. Stream response to CLI
   ↓
13. Log event: narration
   ↓
14. Auto-save session to JSON
```

**Key Points**:
- CLI is thin layer, just routing
- DM Agent makes all narrative decisions
- Tools execute reliably with logging
- Everything persisted immediately

### Example 2: NPC Conversation (Future Multi-Agent)

```
1. DM decides: "The spy reports back to the villain"
   ↓
2. DM Agent → Orchestrator: simulate_npc_conversation(spy, villain)
   ↓
3. Orchestrator:
   - Load Spy agent with personal memories
   - Load Villain agent with their context
   - Set up conversation framework
   ↓
4. Spy Agent → Query: retrieve_personal_memory("what I learned about PCs")
   ↓
5. Spy Agent: "I saw them planning to infiltrate the castle"
   ↓
6. Villain Agent → Evaluate: check_motivation("stop_intruders")
   ↓
7. Villain Agent: "Excellent. Double the guards at the gate."
   ↓
8. Orchestrator → Memory:
   - Log conversation events
   - Update Villain's knowledge state
   - Propagate info through knowledge graph
   ↓
9. DM Agent:
   - Generate world response
   - Update faction state (increased security)
```

**Key Points**:
- Each NPC has isolated knowledge
- Knowledge transfers through explicit conversation
- All interactions logged for consistency
- World state updated based on outcomes

### Example 3: Session Load

```
1. Player: Selects session from list
   ↓
2. CLI: Displays session options
   ↓
3. SessionLog.load(session_id)
   ↓
4. Parse JSON file:
   - Load all scenes
   - Load all events
   - Reconstruct hierarchy
   ↓
5. Build recent context:
   - Get last N events
   - Format for display
   ↓
6. Show player "Previously on..."
   ↓
7. Ready for next input
```

**Key Points**:
- Complete state recovery from JSON
- Smart context display (not overwhelming)
- Ready to continue immediately

## Agent Prompting Strategy

How we structure prompts for different agent types.

### DM Agent System Prompt

```
ROLE: You are the Dungeon Master for a [GENRE] campaign.

CAMPAIGN CONTEXT:
- Setting: [setting_description]
- Tone: [tone_guidance - dark, heroic, comedic, etc.]
- Active Plot Threads: [plot_summary]

CURRENT SITUATION:
- Location: [current_location]
- Present Characters: [pc_list, npc_list]
- Recent Events: [last_3-5_events]
- Time: [in_game_time - day/night, season, etc.]

YOUR RESPONSIBILITIES:
- Describe the world and outcomes of actions
- Play unnamed NPCs and creatures
- Enforce rules fairly and consistently
- Adapt to unexpected player choices
- Maintain narrative pacing and tension
- Use your tools (dice, scenes, state) proactively

PLAYER PREFERENCES:
- Content boundaries: [safety_info]
- Desired challenge level: [difficulty - easy, medium, hard]
- Playstyle: [roleplay_focused, combat_focused, balanced]

TOOLS AVAILABLE:
[tool_descriptions - roll_dice, start_scene, end_scene, log_event]

CURRENT SCENE:
[scene_description]

What happens next?
```

**Design Notes**:
- Context is rich but focused
- Clear responsibilities
- Tools listed and explained
- Player preferences respected

### NPC Agent Prompt (Future)

```
ROLE: You are [NPC_NAME], a [description].

PERSONALITY:
[personality_traits - brave, greedy, cautious, etc.]

GOALS:
- Short-term: [current_goal - get paid, escape, find item]
- Long-term: [ultimate_goal - retire wealthy, revenge, etc.]

RELATIONSHIPS:
[relationship_summary - trusts X, fears Y, loves Z]

WHAT YOU KNOW:
[knowledge_summary - only what this NPC has learned]

CURRENT SITUATION:
[scene_context_from_npc_perspective]

RECENT MEMORIES:
[last_interactions_with_PCs]

EMOTIONAL STATE: [current_feelings - angry, pleased, suspicious]

CONSTRAINTS:
- You don't know anything beyond what's listed above
- You can't read minds or know PC plans
- You must act according to your personality and goals
- You are not aware you're in a game
- Stay in character at all times

TOOLS AVAILABLE:
[limited_npc_tools - speak_to_pc, perform_action, evaluate_trust]

The players are interacting with you. How do you respond?
```

**Design Notes**:
- Strictly limited knowledge
- Clear personality guidance
- Explicit constraints
- No meta-game awareness

## Persistence Layer Details

### Session Database Schema (Future PostgreSQL)

```sql
-- Sessions table
CREATE TABLE sessions (
    id UUID PRIMARY KEY,
    session_id VARCHAR(50) UNIQUE NOT NULL,
    campaign_id UUID REFERENCES campaigns(id),
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    title VARCHAR(200),
    summary TEXT,
    metadata JSONB
);

-- Scenes table
CREATE TABLE scenes (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES sessions(id),
    scene_id VARCHAR(50) NOT NULL,
    title VARCHAR(200),
    location VARCHAR(200),
    participants TEXT[],
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    summary TEXT,
    is_active BOOLEAN DEFAULT false,
    UNIQUE(session_id, scene_id)
);

-- Events table
CREATE TABLE events (
    id UUID PRIMARY KEY,
    scene_id UUID REFERENCES scenes(id),
    timestamp TIMESTAMP NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    actor VARCHAR(100),
    content TEXT NOT NULL,
    metadata JSONB,
    embedding VECTOR(1536) -- For semantic search
);

-- Indexes
CREATE INDEX idx_events_scene ON events(scene_id);
CREATE INDEX idx_events_timestamp ON events(timestamp);
CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_events_actor ON events(actor);
CREATE INDEX idx_events_embedding ON events USING ivfflat (embedding);
```

### Campaign Database Schema (Future)

```sql
-- Campaigns table
CREATE TABLE campaigns (
    id UUID PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    setting TEXT,
    start_date TIMESTAMP NOT NULL,
    game_system VARCHAR(50),
    metadata JSONB
);

-- Plot threads table
CREATE TABLE plot_threads (
    id UUID PRIMARY KEY,
    campaign_id UUID REFERENCES campaigns(id),
    title VARCHAR(200) NOT NULL,
    status VARCHAR(50), -- active, resolved, abandoned
    description TEXT,
    related_events UUID[],
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- World state snapshots
CREATE TABLE world_state_snapshots (
    id UUID PRIMARY KEY,
    campaign_id UUID REFERENCES campaigns(id),
    timestamp TIMESTAMP NOT NULL,
    state_data JSONB NOT NULL,
    snapshot_type VARCHAR(50) -- auto, manual, milestone
);
```

### Character Database Schema (Future)

```sql
-- Characters table
CREATE TABLE characters (
    id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    character_type VARCHAR(50), -- pc, npc, creature
    campaign_id UUID REFERENCES campaigns(id),
    stats JSONB,
    personality JSONB,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- Character memories table
CREATE TABLE character_memories (
    id UUID PRIMARY KEY,
    character_id UUID REFERENCES characters(id),
    content TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    participants TEXT[],
    importance INTEGER, -- 1-10 scale
    embedding VECTOR(1536)
);

-- Character relationships table
CREATE TABLE character_relationships (
    id UUID PRIMARY KEY,
    character_id UUID REFERENCES characters(id),
    other_character_id UUID REFERENCES characters(id),
    relationship_type VARCHAR(50), -- friend, enemy, family, etc.
    strength INTEGER, -- -10 to +10 scale
    notes TEXT,
    UNIQUE(character_id, other_character_id)
);

-- Character knowledge table
CREATE TABLE character_knowledge (
    id UUID PRIMARY KEY,
    character_id UUID REFERENCES characters(id),
    fact TEXT NOT NULL,
    source VARCHAR(200), -- where they learned it
    confidence INTEGER, -- 1-10 scale
    timestamp TIMESTAMP NOT NULL
);
```

### Knowledge Graph Structure (Future)

**Nodes**:
- Characters (PCs, NPCs)
- Locations
- Factions
- Items
- Events
- Concepts (prophecies, legends, etc.)

**Edges**:
- `KNOWS_ABOUT`: Character → Entity (with confidence level)
- `LOCATED_IN`: Character/Item → Location
- `MEMBER_OF`: Character → Faction
- `TRUSTS/FEARS/LOVES`: Character → Character (with strength)
- `HAPPENED_BEFORE`: Event → Event
- `CAUSED_BY`: Event → Character/Faction
- `POSSESSES`: Character → Item
- `CONTROLS`: Faction → Location/Resource

**Queries**:
```cypher
// Find all characters who know about the artifact
MATCH (c:Character)-[k:KNOWS_ABOUT]->(a:Item {name: 'Ancient Artifact'})
WHERE k.confidence > 5
RETURN c, k

// Find connection path between two characters
MATCH path = shortestPath(
  (c1:Character {name: 'Alice'})-[*]-(c2:Character {name: 'Bob'})
)
RETURN path

// Find all factions that control locations near the party
MATCH (pc:Character {type: 'PC'})-[:LOCATED_IN]->(loc:Location)
MATCH (loc)-[:NEAR]->(nearby:Location)<-[:CONTROLS]-(f:Faction)
RETURN DISTINCT f
```

## Content Generation Quality Control

When generating content on-the-fly:

1. **Consistency Check**:
   - Query knowledge graph for existing info
   - Check against established world state
   - Validate no contradictions

2. **Difficulty Calibration**:
   - Consider party level/resources
   - Match to requested challenge
   - Account for player preferences

3. **Genre Matching**:
   - Maintain established tone
   - Use appropriate language/descriptions
   - Follow genre conventions

4. **Uniqueness**:
   - Track recently generated content
   - Avoid repetitive names/descriptions
   - Maintain variety

## Architectural Evolution

### Current (MVP): Simple & Reliable
- Single DM agent
- JSON persistence
- Synchronous operations
- Direct tool calling

### Phase 2: Enhanced & Scalable
- Individual NPC agents
- PostgreSQL database
- Async/await operations
- Orchestrator coordination

### Phase 3: Distributed & Rich
- Multi-agent system
- Vector + graph databases
- Message queue coordination
- Web frontend

### Phase 4: Advanced & Community
- AI-driven content marketplace
- Cross-campaign analytics
- Voice/visual generation
- Platform integrations

Each phase builds on previous architecture without breaking changes.
