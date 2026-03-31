# Project Brief: Tabletop RPG DM Agent System

## Vision

An agentic AI Dungeon Master for tabletop RPGs with intelligent narrative generation, persistent session memory, and tool-based interactions. Acts as a collaborative DM that maintains world state, manages NPCs, handles game mechanics, and adapts to player choices.

## Core Goals

1. **Intelligent DM**: AI that runs engaging tabletop RPG sessions with minimal human oversight
2. **Persistent Memory**: Complete session history with hierarchical organization (Sessions → Scenes → Events)
3. **Tool-Based Interaction**: DM autonomously uses tools (dice rolling, scene management, state tracking)
4. **Game System Agnostic**: Core system works with any RPG, with optional game-specific extensions
5. **Player Agency**: Respect player choices and adapt narrative accordingly

## Target Platform

- **MVP**: Command-line interface (CLI)
- **Future**: Web UI, Discord bot, VTT integrations, multi-player support

## Key Differentiators

- **Streaming Narration**: Real-time text generation for immersive experience
- **Player-Defined Settings**: Players describe their starting scenario
- **Hierarchical Memory**: Scene-based organization instead of flat logs
- **Arbitrary Dice Support**: d3, d7, d25, or any die size
- **Session Resumability**: Complete save/load system with JSON persistence

## Technical Stack

- Python 3.12+, Poetry, Pydantic v2, Rich terminal UI
- Claude Sonnet via OpenRouter (OpenAI-compatible API)
- JSON for session persistence

## Scope

### In Scope (MVP) ✅ Done
- Single-player CLI gameplay
- AI DM with tool calling
- Session logging and resumability
- Dice rolling with full notation support
- Basic game state management

### Out of Scope (Future)
See [futureFeatures.md](futureFeatures.md) for the roadmap.

## Design Philosophy

- **Narrative Coherence**: Stories make sense and feel connected
- **Player Agency**: Player choices matter and shape the narrative
- **Maintainability**: Clean architecture with clear separation of concerns
- **Extensibility**: Easy to add new tools, game systems, and features
