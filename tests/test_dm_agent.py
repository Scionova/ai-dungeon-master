"""Tests for DM Agent."""

import os
from unittest.mock import Mock, MagicMock
import pytest

from rpg_dm.agents import DMAgent
from rpg_dm.config import Config
from rpg_dm.llm import LLMClient, LLMResponse, ChatMessage, ChatRole, ToolCall, FunctionCall
from rpg_dm.memory import SessionLog
from rpg_dm.utilities.dice import DiceRoller, RollResult


@pytest.fixture(autouse=True)
def set_test_env(monkeypatch):
    """Set test environment variables for all tests."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-api-key")


@pytest.fixture
def mock_config():
    """Create mock configuration."""
    config = Mock(spec=Config)
    config.dm_model = "test-model"
    config.temperature = 0.7
    config.max_tokens = 2000
    return config


@pytest.fixture
def mock_llm_client():
    """Create mock LLM client."""
    return Mock(spec=LLMClient)


@pytest.fixture
def session_log(tmp_path):
    """Create session log with temporary path."""
    return SessionLog(session_id="test-session")


@pytest.fixture
def dice_roller():
    """Create dice roller with fixed seed."""
    return DiceRoller(seed=42)


@pytest.fixture
def dm_agent(mock_config, mock_llm_client, session_log, dice_roller):
    """Create DM agent with mocked dependencies."""
    return DMAgent(
        config=mock_config,
        llm_client=mock_llm_client,
        session_log=session_log,
        dice_roller=dice_roller,
    )


class TestDMAgentInitialization:
    """Tests for DM agent initialization."""

    def test_initialization(self, dm_agent, mock_config, mock_llm_client, session_log):
        """Test DM agent initializes correctly."""
        assert dm_agent.config == mock_config
        assert dm_agent.llm_client == mock_llm_client
        assert dm_agent.session_log == session_log
        assert dm_agent.dice_roller is not None
        assert dm_agent.system_prompt is not None
        assert len(dm_agent.system_prompt) > 0

    def test_system_prompt_content(self, dm_agent):
        """Test system prompt contains key elements."""
        prompt = dm_agent.system_prompt
        assert "Dungeon Master" in prompt
        assert "tool" in prompt.lower()
        assert "narrat" in prompt.lower()
        assert "player" in prompt.lower()


class TestDMAgentTools:
    """Tests for DM agent tool definitions."""

    def test_get_tools(self, dm_agent):
        """Test getting tool definitions."""
        tools = dm_agent.get_tools()

        assert len(tools) > 0
        tool_names = [t.function["name"] for t in tools]
        assert "roll_dice" in tool_names
        assert "start_scene" in tool_names
        assert "end_scene" in tool_names
        assert "log_event" in tool_names

    def test_roll_dice_tool_definition(self, dm_agent):
        """Test roll_dice tool has correct schema."""
        tools = dm_agent.get_tools()
        roll_dice_tool = next(t for t in tools if t.function["name"] == "roll_dice")

        assert "notation" in roll_dice_tool.function["parameters"]["properties"]
        assert "purpose" in roll_dice_tool.function["parameters"]["properties"]
        assert "roll_type" in roll_dice_tool.function["parameters"]["properties"]
        assert "notation" in roll_dice_tool.function["parameters"]["required"]

    def test_scene_tools_definition(self, dm_agent):
        """Test scene management tools have correct schema."""
        tools = dm_agent.get_tools()
        tool_names = {t.function["name"]: t for t in tools}

        # Check start_scene
        start_scene = tool_names["start_scene"]
        assert "title" in start_scene.function["parameters"]["properties"]
        assert "location" in start_scene.function["parameters"]["properties"]

        # Check end_scene
        end_scene = tool_names["end_scene"]
        assert "summary" in end_scene.function["parameters"]["properties"]


class TestToolExecution:
    """Tests for tool execution."""

    def test_execute_roll_dice_normal(self, dm_agent, session_log):
        """Test executing normal dice roll."""
        result = dm_agent._execute_tool(
            "roll_dice", {"notation": "d20", "purpose": "Attack roll", "roll_type": "normal"}
        )

        assert "Roll result:" in result
        assert "d20" in result

        # Check event was logged
        events = session_log.get_all_events()
        assert len(events) > 0
        last_event = events[-1]
        assert last_event.event_type == "dice_roll"
        assert "Attack roll" in last_event.content

    def test_execute_roll_dice_advantage(self, dm_agent):
        """Test executing advantage roll."""
        result = dm_agent._execute_tool(
            "roll_dice",
            {"notation": "d20", "purpose": "Perception check", "roll_type": "advantage"},
        )

        assert "Roll result:" in result
        assert "Advantage" in result or "advantage" in result

    def test_execute_roll_dice_arbitrary_size(self, dm_agent):
        """Test rolling arbitrary dice size."""
        result = dm_agent._execute_tool(
            "roll_dice", {"notation": "d25", "purpose": "Random table", "roll_type": "normal"}
        )

        assert "Roll result:" in result
        assert "d25" in result

    def test_execute_start_scene(self, dm_agent, session_log):
        """Test executing start_scene."""
        result = dm_agent._execute_tool(
            "start_scene", {"title": "The Tavern", "location": "Leaky Dragon Inn"}
        )

        assert "Started new scene" in result
        assert "The Tavern" in result

        # Check scene was started
        assert session_log.current_scene is not None
        assert session_log.current_scene.title == "The Tavern"
        assert session_log.current_scene.location == "Leaky Dragon Inn"

    def test_execute_end_scene(self, dm_agent, session_log):
        """Test executing end_scene."""
        # Start a scene first
        session_log.start_scene("Test Scene", "Test Location")

        result = dm_agent._execute_tool(
            "end_scene", {"summary": "The heroes left the tavern."}
        )

        assert "Ended current scene" in result
        assert "The heroes left the tavern" in result

        # Check scene was ended
        assert session_log.current_scene is None or not session_log.current_scene.is_active

    def test_execute_log_event(self, dm_agent, session_log):
        """Test executing log_event."""
        result = dm_agent._execute_tool(
            "log_event",
            {
                "event_type": "npc_dialogue",
                "content": "The guard says 'Halt!'",
                "actor": "Guard",
            },
        )

        assert "Logged" in result
        assert "npc_dialogue" in result

        # Check event was logged
        events = session_log.get_all_events()
        assert any(e.content == "The guard says 'Halt!'" for e in events)

    def test_execute_unknown_tool(self, dm_agent):
        """Test executing unknown tool."""
        result = dm_agent._execute_tool("unknown_tool", {})
        assert "Unknown tool" in result


class TestDMAgentRespond:
    """Tests for DM agent responses."""

    def test_respond_simple_message(self, dm_agent, mock_llm_client, session_log):
        """Test responding to simple player message without tool calls."""
        # Mock LLM response with no tool calls
        mock_response = LLMResponse(
            content="You enter the tavern. It's warm and crowded.",
            tool_calls=None,
            model="test-model",
            usage={"prompt_tokens": 100, "completion_tokens": 50},
        )
        mock_llm_client.chat.return_value = mock_response

        response = dm_agent.respond("I enter the tavern")

        assert response == "You enter the tavern. It's warm and crowded."

        # Check player action was logged
        events = session_log.get_all_events()
        assert any(e.event_type == "player_action" and "enter the tavern" in e.content for e in events)

        # Check DM narration was logged
        assert any(e.event_type == "narration" and e.actor == "DM" for e in events)

    def test_respond_with_tool_call(self, dm_agent, mock_llm_client, session_log):
        """Test responding with tool calls."""
        # First response: tool call
        tool_call = ToolCall(
            id="call_1",
            type="function",
            function=FunctionCall(
                name="roll_dice",
                arguments={"notation": "d20", "purpose": "Attack roll", "roll_type": "normal"},
            ),
        )
        mock_response_1 = LLMResponse(
            content="Rolling for attack...",
            tool_calls=[tool_call],
            model="test-model",
            usage={"prompt_tokens": 100, "completion_tokens": 50},
        )

        # Second response: final narration
        mock_response_2 = LLMResponse(
            content="The attack hits!",
            tool_calls=None,
            model="test-model",
            usage={"prompt_tokens": 120, "completion_tokens": 30},
        )

        mock_llm_client.chat.side_effect = [mock_response_1, mock_response_2]

        response = dm_agent.respond("I attack the goblin")

        assert response == "The attack hits!"

        # Check that chat was called twice (once for initial, once after tool)
        assert mock_llm_client.chat.call_count == 2

        # Check dice roll was logged
        events = session_log.get_all_events()
        assert any(e.event_type == "dice_roll" for e in events)

    def test_respond_builds_context(self, dm_agent, mock_llm_client, session_log):
        """Test that respond builds context from session history."""
        # Add some events to history
        session_log.start_scene("Tavern", "Inn")
        session_log.log_event("narration", "You see a mysterious figure.", "DM", {})

        mock_response = LLMResponse(
            content="The figure looks up.",
            tool_calls=None,
            model="test-model",
            usage={"prompt_tokens": 100, "completion_tokens": 50},
        )
        mock_llm_client.chat.return_value = mock_response

        dm_agent.respond("I approach the figure")

        # Check that chat was called with messages including context
        call_args = mock_llm_client.chat.call_args
        messages = call_args[1]["messages"]

        # Should have system prompt, context, and user message
        assert len(messages) >= 3
        assert any("Session context" in m.content for m in messages if m.content)


class TestDMAgentRespondStream:
    """Tests for streaming DM agent responses."""

    def test_respond_stream_simple(self, dm_agent, mock_llm_client, session_log):
        """Test streaming response without tool calls."""
        from rpg_dm.llm import StreamChunk

        # Mock streaming response
        chunks = [
            StreamChunk(content="You enter ", tool_calls=None, finish_reason=None),
            StreamChunk(content="the tavern.", tool_calls=None, finish_reason="stop"),
        ]
        mock_llm_client.chat_stream.return_value = iter(chunks)

        result = list(dm_agent.respond_stream("I enter the tavern"))

        assert "".join(result) == "You enter the tavern."

        # Check narration was logged
        events = session_log.get_all_events()
        assert any(
            e.event_type == "narration" and "You enter the tavern" in e.content for e in events
        )

    def test_respond_stream_with_tool_calls(self, dm_agent, mock_llm_client, session_log):
        """Test streaming response with tool calls."""
        from rpg_dm.llm import StreamChunk

        tool_call = ToolCall(
            id="call_1",
            type="function",
            function=FunctionCall(
                name="roll_dice",
                arguments={"notation": "d20", "purpose": "Attack", "roll_type": "normal"},
            ),
        )

        # First stream: content + tool call
        chunks_1 = [
            StreamChunk(content="Rolling...", tool_calls=None, finish_reason=None),
            StreamChunk(content=None, tool_calls=[tool_call], finish_reason="tool_calls"),
        ]

        # Second stream: final narration
        chunks_2 = [
            StreamChunk(content="Hit!", tool_calls=None, finish_reason="stop"),
        ]

        mock_llm_client.chat_stream.side_effect = [iter(chunks_1), iter(chunks_2)]

        result = list(dm_agent.respond_stream("I attack"))

        # Should contain initial content, tool result, and final content
        full_result = "".join(result)
        assert "Rolling..." in full_result
        assert "roll_dice" in full_result
        assert "Hit!" in full_result
