# Product Context: Tabletop RPG DM Agent System

## Why This Exists

Tabletop RPGs are incredibly fun but face several challenges:

1. **DM Availability**: Finding a skilled, available DM is difficult
2. **Prep Time**: DMs spend hours preparing sessions
3. **Consistency**: Human DMs can forget details or lose track of plot threads
4. **Solo Play**: Playing solo RPGs lacks the dynamic response of a real DM
5. **Learning Curve**: New players struggle to learn complex rule systems

This system aims to make high-quality RPG experiences accessible to anyone, anytime, while reducing DM workload and maintaining narrative quality.

## Problems We Solve

### For Solo Players
- Provides an intelligent, responsive DM for solo play
- Adapts to player choices in real-time
- Maintains complete session memory
- Never forgets details or continuity

### For Game Masters
- Reduces prep time with automated content generation (future)
- Maintains perfect session logs automatically
- Handles mechanical lookups and calculations
- Provides consistent NPC personalities (future)

### For New Players
- Guides players through character creation and gameplay
- Explains rules as needed
- Adapts difficulty to player skill level (future)
- Provides a safe space to learn

## How It Works

### User Experience Flow

1. **Start**: Player launches the CLI and sees main menu
2. **Create or Load**: Choose to start new game or load saved session
3. **Character Creation**: Enter character name and description
4. **Set the Scene**: Describe where and how the adventure begins
5. **Play**: Interact naturally with the DM through text
6. **Save**: Sessions auto-save; can manually save or save on exit
7. **Resume**: Load any previous session to continue the adventure

### Key Interactions

#### Natural Language Play
```
Player: I examine the ancient door for traps
DM: [Rolls perception check automatically]
    You run your fingers along the doorframe, noting the dust patterns...
```

#### Commands During Play
- `/roll d20+5` - Manual dice rolling
- `/state` - View current game state
- `/save` - Save progress
- `/exit` - Return to menu (with save prompt)

#### DM Tool Usage
The DM automatically:
- Rolls dice when needed
- Starts new scenes for narrative breaks
- Logs all events with timestamps
- Tracks game state (location, NPCs, etc.)

## User Experience Goals

### Immersion
- **Streaming narration** creates suspense
- **Rich terminal formatting** with colors and styling
- **Natural language** interaction (no rigid command syntax)
- **Scene-based narrative** with clear transitions

### Transparency
- Show all dice rolls and results
- Display tool usage (scene starts, state changes)
- Clear feedback for all actions
- Visible save/load operations

### Player Control
- Player defines starting scenario
- Natural language input for maximum flexibility
- Commands for direct control (/roll, /state, etc.)
- Prompts before saving to respect player preferences

### Reliability
- Auto-saves after every event
- Full session recovery from JSON files
- Clear error messages
- Graceful handling of interruptions

## Target Audience

### Primary Users (MVP)
- **Solo RPG Enthusiasts**: People who want to play RPGs alone
- **System Explorers**: Players wanting to try new game systems without a group
- **Story Seekers**: People interested in interactive fiction with game mechanics

### Secondary Users (Future)
- **Game Masters**: Looking for prep assistance and session tools
- **New Players**: Learning RPG systems
- **Game Designers**: Testing scenarios and mechanics
- **Content Creators**: Generating actual play content

## Differentiation from Alternatives

### vs AI Dungeon / NovelAI
- ✅ **Structured game mechanics** (not just freeform storytelling)
- ✅ **Persistent structured state** (characters, inventory, world state)
- ✅ **Tool-based interactions** (dice, scenes, state management)
- ✅ **Session resumability** with complete history

### vs Virtual Tabletops (Roll20, Foundry)
- ✅ **No human DM required**
- ✅ **AI-driven narrative** adapts to player choices
- ✅ **Automated session logging** with scene hierarchy
- ❌ No visual maps (future feature)
- ❌ No multi-player (future feature)

### vs Solo RPG Systems (Mythic GME, Ironsworn)
- ✅ **Natural language interaction** vs oracle tables
- ✅ **Coherent narrative** vs random prompts
- ✅ **Automated mechanics** vs manual tracking
- ✅ **Rich descriptions** vs interpretation work

## Metrics for Success

### Engagement
- Session length (longer = more engaging)
- Number of sessions per user
- Return rate (users loading saved games)

### Quality
- Narrative coherence (qualitative assessment)
- Player satisfaction surveys
- Successful tool usage rate

### Technical
- Session save/load success rate
- Tool calling accuracy
- Response streaming performance
- Error rate and recovery

## Future Vision

For detailed development phases, roadmap, and technology decisions, see [futureFeatures.md](futureFeatures.md).

**Quick Summary**:
- **Phase 2 (3-6 months)**: Quest tracking, clocks, NPC agents, enhanced features
- **Phase 3 (6-12 months)**: Web interface, multi-player, content generation
- **Phase 4 (12-24 months)**: Voice, VTT integrations, mobile, community features

## Risks and Mitigations

For comprehensive risk analysis and mitigation strategies, see [futureFeatures.md](futureFeatures.md#risk-mitigation).
