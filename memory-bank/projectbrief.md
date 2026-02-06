# Project Brief: Tabletop RPG DM Agent System

## Vision

An agentic AI Dungeon Master system for tabletop RPGs that provides intelligent narrative generation, persistent session memory, and tool-based interactions. The system acts as a collaborative DM that maintains world state, manages NPCs, handles game mechanics, and adapts to player choices while preserving player agency.

## Core Goals

1. **Intelligent DM**: Create an AI that can run engaging tabletop RPG sessions with minimal human oversight
2. **Persistent Memory**: Maintain complete session history with hierarchical organization (Sessions → Scenes → Events)
3. **Tool-Based Interaction**: Enable the DM to autonomously use tools (dice rolling, scene management, state tracking)
4. **Game System Agnostic**: Core system works with any RPG, with optional game-specific extensions
5. **Player Agency**: Respect player choices and adapt narrative accordingly

## Target Platform

- **MVP**: Linux command-line interface (CLI)
- **Future**: Web UI, Discord bot, VTT integrations, multi-player support

## Key Differentiators

- **Streaming Narration**: Real-time text generation for immersive experience
- **Player-Defined Settings**: Players describe their starting scenario
- **Hierarchical Memory**: Scene-based organization instead of flat logs
- **Arbitrary Dice Support**: d3, d7, d25, or any die size
- **Session Resumability**: Complete save/load system with JSON persistence

## Success Criteria

- Players can start and play a complete session with the AI DM
- System maintains narrative coherence across multiple sessions
- DM automatically uses tools without manual intervention
- Session state is fully recoverable from saved files
- System adapts to unexpected player actions gracefully

## Scope Boundaries

### In Scope (MVP)
- Single-player CLI gameplay
- AI-powered DM with tool calling
- Session logging and resumability
- Dice rolling with full notation support
- Basic game state management
- Player-defined starting scenarios

### Out of Scope (Future)
- Multi-player support
- Individual NPC agents
- Faction systems
- Campaign arc management
- Web or mobile interfaces
- VTT integrations
- Voice interfaces

## Technical Constraints

- Python-based implementation
- Uses Claude 4.5 Sonnet via OpenRouter
- JSON for session persistence
- Pydantic for data validation
- Rich library for terminal UI
- Poetry for dependency management

## Design Philosophy

The system prioritizes:
- **Narrative Coherence**: Stories make sense and feel connected
- **Player Agency**: Player choices matter and shape the narrative
- **Adaptability**: Handle unexpected player actions gracefully
- **Maintainability**: Clean architecture with clear separation of concerns
- **Extensibility**: Easy to add new tools, game systems, and features
