# Future Features & Planning

This document outlines planned features, technology decisions, and open questions for future development of the Tabletop RPG DM Agent System.

## Development Phases

### Phase 1: MVP (Minimum Viable Product) ✅ *COMPLETED*
- ✅ Single-player text interface
- ✅ DM agent only (no individual NPC agents)
- ✅ Basic memory system (hierarchical log)
- ✅ Comprehensive dice rolling
- ✅ Manual turn management
- ✅ Game-system agnostic core

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
- [ ] Web interface (React/Next.js)
- [ ] Multiple game system support
- [ ] Multi-player support (2-6 players)
- [ ] Discord bot integration
- [ ] Safety tools and content filtering

### Phase 4: Advanced Features (12-24 months)
- [ ] Voice interface integration
- [ ] Visual content generation (maps, portraits)
- [ ] VTT platform integrations (Roll20, Foundry)
- [ ] Analytics and insights dashboard
- [ ] Mobile app (React Native)
- [ ] Community features (share campaigns, rate content)
- [ ] Marketplace for custom content
- [ ] Advanced AI features (predictive content, adaptive difficulty)

## Technology Stack Recommendations

### Core Framework
**Current**: Python 3.12+ with Poetry

**Alternatives Considered**:
- **Node.js**: Better real-time performance, larger ecosystem for web
- **LangChain/LlamaIndex**: Agent orchestration frameworks
  - Pros: Built-in agent patterns, tool calling, memory management
  - Cons: Abstraction overhead, rapid API changes
  - Decision: Consider for Phase 2+ when multi-agent orchestration needed

### LLM Providers
**Current**: OpenRouter → Claude 4.5 Sonnet

**Future Options**:
- **OpenAI GPT-4**: Strong reasoning, good tool calling
- **Anthropic Claude**: Excellent safety, longer context windows
- **Local Models**: Llama 3, Mistral, Mixtral
  - Via Ollama for local deployment
  - Cost savings for high usage
  - Privacy benefits
  - Performance trade-off

**Recommendation**: Maintain OpenRouter for flexibility, add local model support in Phase 2

### Databases

**Current**: JSON file storage

**Phase 2 Migration**:
- **PostgreSQL**: Primary relational store
  - Sessions, campaigns, characters
  - JSONB for flexible game state
  - Full-text search capability
  - Battle-tested, reliable

**Phase 3 Additions**:
- **Vector Database**: Semantic search
  - Options: Pinecone (cloud), Weaviate (self-hosted), ChromaDB (embedded)
  - For memory retrieval and content similarity
  - Essential for long campaigns

- **Graph Database** (Optional): Knowledge relationships
  - Neo4j for rich relationship queries
  - Character networks, plot connections
  - May be overkill unless building complex simulations

### Infrastructure

**Phase 2 (API Layer)**:
- **FastAPI**: Python async web framework
  - OpenAPI docs auto-generation
  - WebSocket support for real-time
  - Type hints and Pydantic integration

**Phase 2 (Caching)**:
- **Redis**: In-memory cache and pub/sub
  - LLM response caching
  - Session state caching
  - Real-time updates via pub/sub

**Phase 3 (Scaling)**:
- **Docker**: Containerization for consistent deployment
- **Message Queue**: RabbitMQ or Redis Streams
  - Agent coordination at scale
  - Background job processing
  - Event-driven architecture

### Frontend

**Phase 3 (Web Interface)**:
- **React + Next.js**: Modern web framework
  - Server-side rendering for SEO
  - API routes for backend
  - TypeScript for type safety

- **Socket.io**: Real-time bidirectional communication
  - Streaming DM responses
  - Multi-player coordination
  - Live updates

- **TailwindCSS + shadcn/ui**: Rapid UI development

**Phase 4 (Mobile)**:
- **React Native**: Cross-platform mobile
  - Code sharing with web
  - Native performance

**Phase 4 (Integrations)**:
- **Discord.py**: Discord bot integration
- **VTT APIs**: Roll20, Foundry plugins

## Open Questions & Design Decisions

### 1. Agent Autonomy vs Control
**Question**: How much should the DM agent act independently vs waiting for human approval?

**Options**:
- A) Fully autonomous (agent decides everything)
- B) Confirm major changes (story beats, character deaths)
- C) Suggest and wait for approval
- D) Configurable per-session

**Leaning Toward**: D - Let players/DMs set their preferred level

### 2. NPC Agent Threshold
**Question**: What level of importance triggers individual NPC agent vs DM handling?

**Criteria to Consider**:
- Named vs unnamed
- Conversation depth
- Relationship importance
- Computational cost

**Leaning Toward**: Named NPCs with >3 interactions get dedicated agents

### 3. Memory Retention
**Question**: How aggressively to compress old memories? Risk losing important details.

**Strategy**:
- Keep full detail: Last 5 scenes
- Scene summaries: Scenes 6-20
- Session summaries: Beyond 20 scenes
- Never compress: Flagged "important" events

**Trade-off**: Storage vs accuracy

### 4. Consistency vs Creativity
**Question**: Balance between maintaining consistency and allowing interesting contradictions/surprises?

**Approach**:
- Hard consistency: Character stats, past events
- Soft consistency: NPC motivations (can evolve)
- Creative freedom: Descriptions, narrative tone
- Contradiction detection: Alert but don't block

### 5. Cost Management
**Question**: LLM API costs could be high for long campaigns. How to optimize?

**Strategies**:
- Use smaller models for routine tasks (Haiku for simple NPCs)
- Aggressive caching (deduplicate similar queries)
- Local model option for cost-sensitive users
- Token budget per session
- Batch API calls where possible

**Target**: <$1 per hour of gameplay

### 6. Multi-Player Sync
**Question**: How to handle simultaneous player actions? Pure turn-based or allow interruptions?

**Options**:
- A) Strict turn-based (combat-style)
- B) Free-form with interrupt system
- C) Hybrid: turn-based in combat, free-form in RP
- D) DM configurable

**Leaning Toward**: C - Hybrid based on situation

### 7. DM Override
**Question**: Should human DM be able to override any agent decision? How to implement cleanly?

**Implementation**:
- `/override` command in CLI/web
- Edit history feature
- Rollback to previous state
- AI learns from overrides (maybe)

**Answer**: Yes, full override capability essential

### 8. Rules Interpretation
**Question**: When rules are ambiguous, does DM agent decide or escalate to human?

**Approach**:
- Clear rules: Agent decides automatically
- Ambiguous: Present options to human DM
- House rules: Configurable per-campaign
- Rule learning: Track decisions for consistency

### 9. Content Rating
**Question**: How to automatically tag generated content for safety/comfort?

**System**:
- Pre-generate content rating before displaying
- Use separate "safety classifier" LLM call
- Player-configured boundaries
- Pause and reroute on boundary violation

**Essential for**: Public/shared campaigns

### 10. Campaign Portability
**Question**: Can campaigns be exported/imported? Shared between groups?

**Format**:
- Standard JSON/YAML export
- Sanitize private player info
- Include world state, NPCs, quests
- Platform-agnostic format
- Sharing marketplace (Phase 4)

**Decision**: Yes, prioritize in Phase 3

## Scaling Considerations

### Token Management

**Challenge**: Limited context windows for LLM agents (200K tokens for Claude)

**Strategies**:
1. **Progressive Compression**:
   - Full detail: Current scene
   - Medium detail: Last N scenes
   - Summaries: Older scenes
   - Key facts: Ancient history

2. **Semantic Search**:
   - Embed all events in vector DB
   - Retrieve only relevant context
   - Score by recency + relevance

3. **Smart Summarization**:
   - Identify important vs mundane
   - Preserve emotional moments
   - Keep character-defining events

4. **Caching**:
   - Cache frequently accessed data
   - Reuse embeddings
   - Cache LLM responses for similar queries

5. **Smaller Models**:
   - Use Haiku for simple tasks
   - Reserve Sonnet for complex reasoning

### Agent Lifecycle

**Challenge**: Can't keep all NPCs loaded simultaneously

**Solution - Three-Tier System**:

1. **Hot** (In Memory):
   - Currently active NPCs
   - Full context loaded
   - Immediate response

2. **Warm** (Cached):
   - Recently used NPCs
   - Summarized state in Redis
   - Quick reload (<1s)

3. **Cold** (Database):
   - Historical NPCs
   - Stored in PostgreSQL
   - Reconstruct from DB (2-5s)

**Trigger Rules**:
- NPC enters scene → Warm to Hot
- NPC exits scene → Hot to Warm
- No interaction 10+ minutes → Warm to Cold
- Re-encounter → Cold to Hot (via Warm)

### Consistency at Scale

**Challenge**: Multiple agents making decisions simultaneously

**Solutions**:

1. **Single Source of Truth**:
   - State Manager as authoritative
   - All state changes through manager
   - Optimistic locking for conflicts

2. **Event Sourcing**:
   - All changes as events
   - Replay for debugging
   - Time-travel debugging

3. **Conflict Detection**:
   - Validate state changes
   - Detect contradictions
   - Rollback on conflict

4. **Audit Trail**:
   - Log all agent decisions
   - Track reasoning
   - Enable debugging

### Performance

**Bottlenecks**:
- LLM API latency (1-3s per call)
- Vector search performance (for large campaigns)
- Database query speed (for complex state)

**Optimizations**:

1. **Parallel Execution**:
   - Multiple agents in parallel when independent
   - Batch similar LLM calls
   - Async/await for I/O

2. **Caching Layers**:
   - LLM response cache (identical prompts)
   - Database query cache
   - Computed result cache

3. **Pre-generation**:
   - Generate content ahead of time
   - Prepare for likely player actions
   - Background processing

4. **Streaming**:
   - Stream LLM responses immediately
   - Don't wait for complete response
   - Better perceived performance

5. **Query Optimization**:
   - Index database properly
   - Minimize N+1 queries
   - Use database-level aggregations

**Performance Targets**:
- First token: <500ms
- Full response: <3s
- State update: <100ms
- Session load: <1s

## Risk Mitigation

### Technical Risks

1. **High API Costs**:
   - Mitigation: Local model fallback, aggressive caching
   - Monitoring: Track costs per session
   - Circuit breaker: Pause at cost threshold

2. **Context Window Limits**:
   - Mitigation: Compression, semantic search
   - Monitoring: Track token usage
   - Fallback: Aggressive summarization

3. **API Reliability**:
   - Mitigation: Retry logic, fallback providers
   - Monitoring: Track API uptime
   - Graceful degradation: Reduced features on failure

### Product Risks

1. **Narrative Quality Issues**:
   - Mitigation: Extensive prompt engineering
   - Feedback loop: User ratings
   - Human review: Option for DM approval

2. **Player Engagement Drop**:
   - Mitigation: Pacing analysis, adaptive difficulty
   - Monitoring: Session length, return rate
   - Adjustment: Dynamic tone/complexity

3. **Complexity Overwhelm**:
   - Mitigation: Progressive disclosure of features
   - Onboarding: Tutorial mode
   - Presets: Simple/Advanced modes

## Next Milestones

### Milestone 1: Enhanced Tracking (Target: 2-3 weeks)
- Quest tracking system
- Clock mechanics
- Enhanced character sheets
- Session search

### Milestone 2: NPC Enhancement (Target: 1-2 months)
- Individual NPC profiles
- NPC memory tracking
- Relationship system
- NPC conversation simulation

### Milestone 3: Web Interface (Target: 3-4 months)
- API layer with FastAPI
- React frontend
- WebSocket for real-time
- User authentication

### Milestone 4: Multi-Player (Target: 4-6 months)
- Database migration
- Multi-player turn management
- Shared session state
- Discord integration

## References

For current implementation status, see:
- [progress.md](progress.md) - What's implemented now
- [activeContext.md](activeContext.md) - Current work focus
- [systemPatterns.md](systemPatterns.md) - Complete technical architecture
