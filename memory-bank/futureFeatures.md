# Future Features & Planning

## Development Phases

### Phase 1: MVP ✅ Complete
- Single-player CLI, DM agent, basic memory, dice rolling, session save/load

### Phase 2: Core Features (Next 3-6 months)
- [ ] Quest tracking system
- [ ] Clock mechanics (Blades in the Dark + generic)
- [ ] Enhanced character sheets
- [ ] Session search and filtering
- [ ] Memory compression/summarization
- [ ] Individual NPC agents with isolated memory
- [ ] Basic faction system
- [ ] Automated turn management

### Phase 3: Enhanced Experience (6-12 months)
- [ ] Knowledge graph for relationships
- [ ] Campaign arc planning and tracking
- [ ] Content generation tools (locations, NPCs, encounters, loot)
- [ ] Web interface (React/Next.js + FastAPI)
- [ ] Multiple game system support
- [ ] Multi-player support (2-6 players)
- [ ] Discord bot integration
- [ ] Safety tools and content filtering

### Phase 4: Advanced Features (12-24 months)
- [ ] Voice interface
- [ ] Visual content generation (maps, portraits)
- [ ] VTT platform integrations (Roll20, Foundry)
- [ ] Mobile app
- [ ] Community features and content marketplace
- [ ] Adaptive difficulty and predictive content

## Open Design Questions

1. **Agent Autonomy**: How much should the DM act independently vs. confirm major changes? → Leaning toward configurable per-session

2. **NPC Agent Threshold**: What triggers a dedicated NPC agent vs. DM handling? → Named NPCs with 3+ interactions

3. **Memory Retention**: How aggressively to compress old memories?
   - Keep full detail: last 5 scenes
   - Scene summaries: scenes 6–20
   - Session summaries: beyond 20 scenes
   - Never compress: flagged "important" events

4. **Multi-Player Sync**: Strict turn-based, free-form, or hybrid? → Hybrid (turn-based in combat, free-form in RP)

5. **DM Override**: Full `/override` command + rollback capability — essential

6. **Rules Interpretation**: Clear rules → agent decides. Ambiguous → present options to human DM.

7. **Cost Management**: Target <$1/hour of gameplay. Use smaller models (Haiku) for routine tasks, add local model support in Phase 2.

8. **Campaign Portability**: Standard JSON/YAML export with world state, NPCs, quests — prioritize in Phase 3.
