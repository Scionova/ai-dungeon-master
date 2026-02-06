# Tech Context: Tabletop RPG DM Agent System

## Technology Stack

### Core Language & Framework
- **Python 3.12+**: Primary implementation language
- **Type Hints**: Full type annotation for IDE support and validation
- **Async/Await**: Support for concurrent operations (future)

### Key Libraries

#### LLM & AI
- **openai** (v1.59.5): OpenAI-compatible client for API calls
- **OpenRouter**: LLM provider (Claude, GPT access via single API)
- **Claude 4.5 Sonnet**: Primary DM model (intelligent, creative)
- **Claude 4 Haiku**: Planned for NPC agents (fast, cost-effective)

#### Data & Validation
- **pydantic** (v2.10.5): Data validation and settings management
- **pydantic-settings**: Environment variable loading
- **python-dotenv** (v1.0.1): .env file support

#### CLI & Display
- **rich** (v13.9.4): Beautiful terminal output with colors, tables, markdown

#### Development Tools
- **pytest** (v8.3.4): Testing framework
- **pytest-asyncio** (v0.25.2): Async test support
- **black**: Code formatting
- **ruff**: Linting and code quality
- **mypy**: Static type checking (future)

### Dependency Management
- **Poetry** (v1.8+): Package management and virtual environments
  - `pyproject.toml`: Project metadata and dependencies
  - `poetry.lock`: Lock file for reproducible builds

## Project Structure

```
src/rpg_dm/
├── __init__.py              # Package initialization
├── config.py                # Configuration management (Pydantic)
│
├── llm/                     # LLM client abstraction
│   ├── __init__.py
│   ├── client.py           # OpenAI-compatible client wrapper
│   └── types.py            # Message types, tool definitions
│
├── memory/                  # Session and memory management
│   ├── __init__.py
│   └── session_log.py      # Hierarchical event logging
│
├── utilities/               # Helper functions and utilities
│   ├── __init__.py
│   └── dice.py             # Dice rolling with full notation support
│
├── agents/                  # AI agents
│   ├── __init__.py
│   └── dm_agent.py         # DM agent with tool calling
│
├── game_state/              # Game state management
│   ├── __init__.py
│   └── game_state.py       # Character, world state tracking
│
└── cli/                     # Command-line interface
    ├── __init__.py
    └── game_cli.py          # Menu system, game loop

tests/
├── __init__.py
├── test_dice.py             # Dice rolling tests (32 tests)
└── test_dm_agent.py         # DM agent tests (17 tests)

data/                        # Runtime data (not in git)
└── sessions/                # Session JSON files
    └── YYYYMMDD_HHMMSS.json

gamesystems/                 # Game system specific content
└── blades_in_the_dark/     # Future: BitD specific mechanics

memory-bank/                 # Memory Bank documentation
├── projectbrief.md
├── productContext.md
├── systemPatterns.md
├── techContext.md           # This file
├── activeContext.md
├── progress.md
└── tasks/
    └── _index.md
```

## Development Setup

### Prerequisites
- Python 3.12 or higher
- Poetry 1.8 or higher
- OpenRouter API key

### Installation

```bash
# Clone repository
git clone <repository-url>
cd ai-dungeon-master

# Install dependencies
poetry install

# Install dev dependencies
poetry install --with dev

# Copy environment template
cp .env.example .env

# Add API key to .env
# OPENROUTER_API_KEY=your_key_here
```

### Running the Application

```bash
# Using Poetry
poetry run rpg-dm

# Or with Python module syntax
poetry run python -m rpg_dm.cli.game_cli
```

### Running Tests

```bash
# All tests
poetry run pytest

# With coverage
poetry run pytest --cov=src

# Specific test file
poetry run pytest tests/test_dice.py

# Verbose output
poetry run pytest -v
```

### Code Quality

```bash
# Format code
poetry run black src/ tests/

# Lint code
poetry run ruff check src/ tests/

# Type check (when mypy added)
poetry run mypy src/
```

## Configuration Management

### Environment Variables (.env)

```bash
# Required
OPENROUTER_API_KEY=sk-or-v1-...

# Optional - LLM Configuration
DM_MODEL=anthropic/claude-sonnet-4-20250514
NPC_MODEL=anthropic/claude-4-haiku-20250514  # Future
TEMPERATURE=0.7
MAX_TOKENS=4000

# Optional - System Configuration  
DATA_DIR=data
LOG_LEVEL=INFO
```

### Config Class (Pydantic)

```python
# src/rpg_dm/config.py
class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )
    
    # API Configuration
    openrouter_api_key: str
    dm_model: str = "anthropic/claude-sonnet-4-20250514"
    
    # System Configuration
    data_dir: Path = Path("data")
    sessions_dir: Path = Field(default=None)
    
    # Validation
    @field_validator("openrouter_api_key")
    def validate_api_key(cls, v):
        if not v or v == "your_api_key_here":
            raise ValueError("Must set OPENROUTER_API_KEY")
        return v
    
    @model_validator(mode="after")
    def set_sessions_dir(self):
        if self.sessions_dir is None:
            self.sessions_dir = self.data_dir / "sessions"
        return self
```

## Data Models

### Pydantic Models

```python
# LLM Messages
class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

# Tool Definitions
class FunctionDefinition(BaseModel):
    name: str
    description: str
    parameters: dict

# Game State
class PlayerCharacter(BaseModel):
    name: str
    description: str = ""
    stats: dict[str, Any] = {}
    inventory: list[str] = []

# Dice Rolls
class RollResult(BaseModel):
    notation: str
    rolls: list[int]
    modifier: int
    total: int
    roll_type: str
    description: str
```

### JSON Schema Examples

**Session JSON Structure**:
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
        },
        {
          "timestamp": "2026-02-06T11:29:36.123456",
          "event_type": "dice_roll",
          "actor": "DM",
          "content": "Perception check: 15",
          "metadata": {
            "notation": "1d20+3",
            "total": 15,
            "roll_type": "normal"
          }
        }
      ]
    }
  ]
}
```

## API Integration

### OpenRouter API

**Base Configuration**:
```python
client = OpenAI(
    api_key=config.openrouter_api_key,
    base_url="https://openrouter.ai/api/v1"
)
```

**Chat Completion**:
```python
response = client.chat.completions.create(
    model=config.dm_model,
    messages=messages,
    tools=tools,  # Tool definitions
    temperature=0.7,
    max_tokens=4000,
    stream=True  # For streaming responses
)
```

**Streaming Response**:
```python
for chunk in response:
    if chunk.choices[0].delta.content:
        yield chunk.choices[0].delta.content
```

### Rate Limits & Cost Management

- **Claude 4.5 Sonnet**: ~$3 per million input tokens, ~$15 per million output tokens
- **Rate Limits**: Varies by tier (check OpenRouter dashboard)

**Optimization Strategies**:
- Use smaller models for routine tasks
- Cache frequently accessed data
- Compress old memories
- Smart context building (only include relevant events)

## Testing Infrastructure

### Pytest Configuration

```python
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

### Test Fixtures

```python
@pytest.fixture
def config():
    """Test configuration with mock API key"""
    return Config(openrouter_api_key="test_key")

@pytest.fixture
def session_log(tmp_path):
    """Session log in temporary directory"""
    return SessionLog(
        session_id="test_session",
        data_dir=tmp_path
    )

@pytest.fixture
def dm_agent(config, session_log):
    """DM agent for testing"""
    return DMAgent(config, session_log)
```

### Mocking LLM Calls

```python
@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    return {
        "id": "test-id",
        "choices": [{
            "message": {
                "role": "assistant",
                "content": "Test response"
            },
            "finish_reason": "stop"
        }]
    }
```

## Performance Considerations

### Current Performance

- **Session Load**: < 100ms for typical sessions
- **LLM Response**: 1-3 seconds (depends on OpenRouter)
- **Streaming Start**: < 500ms (first token)
- **Dice Roll**: < 1ms

### Optimization Targets

- Keep context building under 50ms
- Stream first token within 500ms
- Auto-save under 100ms
- Command processing under 10ms

## Technical Constraints

### MVP Constraints

1. **Single Player**: No concurrent session support
2. **CLI Only**: Terminal-based interface
3. **Linux Target**: Developed and tested on Linux
4. **Internet Required**: OpenRouter API access needed
5. **JSON Storage**: File-based persistence

### Future Scalability Considerations

1. **Multi-Player**: Will need database (PostgreSQL)
2. **Web UI**: Will need API layer and authentication
3. **Real-time**: Will need WebSocket support
4. **Large Campaigns**: Will need memory compression

## Security & Privacy

### Current Implementation

- API keys in .env (not committed to git)
- Session data stored locally
- No user authentication (single player)
- No network communication except OpenRouter API

### Future Considerations

- User authentication for web version
- Session encryption for sensitive content
- Rate limiting and abuse prevention
- Content filtering and moderation

## Deployment

### MVP Deployment

Currently: Local installation only

```bash
# User installs with Poetry
poetry install

# Or with pip
pip install -r requirements.txt

# Runs locally
poetry run rpg-dm
```

### Future Deployment Options

1. **Packaged Binary**: PyInstaller for standalone executable
2. **Docker**: Containerized deployment
3. **Web Service**: FastAPI + React frontend
4. **Cloud**: AWS/GCP/Azure deployment

## Monitoring & Logging

### Current Logging

```python
# Structured logging with metadata
event = {
    "timestamp": datetime.now().isoformat(),
    "event_type": "dice_roll",
    "actor": "DM",
    "content": "Rolled d20: 15",
    "metadata": {"notation": "d20", "total": 15}
}
```

### Future Monitoring

- Application performance monitoring (APM)
- Error tracking (Sentry)
- Usage analytics
- LLM token usage tracking
- Cost monitoring

## Known Technical Debt

1. **No async support**: All LLM calls are synchronous
2. **Limited error handling**: Need better retry logic
3. **No caching**: Every LLM call hits API
4. **Manual context building**: Could be optimized
5. **No compression**: Old sessions grow large
6. **Hard-coded paths**: Some paths not configurable

## Upgrade Path

### Short-term (Next Release)

- Add mypy for static type checking
- Implement retry logic for API calls
- Add caching layer (Redis or local)
- Improve error messages

### Mid-term (3-6 months)

- Migrate to async/await
- Add database support (PostgreSQL)
- Implement memory compression
- Add API layer for web UI

### Long-term (6-12 months)

- Full web application
- Multi-player support
- Real-time collaboration
- Voice interface integration
