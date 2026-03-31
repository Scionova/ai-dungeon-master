# Product Context: Tabletop RPG DM Agent System

## Why This Exists

Tabletop RPGs are fun but face challenges: finding an available DM is hard, prep takes hours, and solo play lacks dynamic response. This system makes high-quality RPG experiences accessible to anyone, anytime.

## Problems We Solve

- **Solo Players**: Intelligent, responsive DM for solo play that never forgets continuity
- **Game Masters**: Automated session logs, mechanical lookups, consistent NPC behavior (future)
- **New Players**: Rule explanations and adaptive difficulty (future)

## User Experience Flow

1. **Start**: Launch CLI, see main menu
2. **Create or Load**: Start new game or load saved session
3. **Character Creation**: Enter character name and description
4. **Set the Scene**: Describe where and how the adventure begins
5. **Play**: Interact naturally with the DM through text
6. **Save/Resume**: Sessions auto-save; load any previous session to continue

## Key Interactions

### Natural Language Play
```
Player: I examine the ancient door for traps
DM: [Rolls perception check automatically]
    You run your fingers along the doorframe, noting the dust patterns...
```

### Commands During Play
- `/roll d20+5` - Manual dice rolling
- `/state` - View current game state
- `/save` - Save progress
- `/exit` - Return to menu (with save prompt)

### DM Tool Usage
The DM automatically rolls dice, starts new scenes, logs events, and tracks game state.

## UX Goals

- **Immersion**: Streaming narration, rich terminal formatting, scene-based narrative
- **Transparency**: Show all dice rolls, tool usage, and save/load operations
- **Player Control**: Natural language input, direct commands, prompts before saving
- **Reliability**: Auto-saves after every event, full session recovery from JSON

## Target Audience

### Primary (MVP)
- Solo RPG enthusiasts, system explorers, interactive fiction fans

### Secondary (Future)
- Game Masters looking for prep assistance, new players learning systems, content creators
