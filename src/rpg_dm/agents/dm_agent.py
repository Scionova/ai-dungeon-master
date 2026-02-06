"""DM Agent - Primary orchestrator and world manager."""

from typing import Iterator, Optional

from rpg_dm.config import Config
from rpg_dm.llm import LLMClient, ChatMessage, ChatRole, StreamChunk, Tool
from rpg_dm.memory import SessionLog
from rpg_dm.utilities.dice import DiceRoller


class DMAgent:
    """The Dungeon Master agent that orchestrates the game."""

    def __init__(
        self,
        config: Config,
        llm_client: LLMClient,
        session_log: SessionLog,
        dice_roller: Optional[DiceRoller] = None,
    ):
        """Initialize DM agent.

        Args:
            config: Application configuration
            llm_client: LLM client for making API calls
            session_log: Session log for memory management
            dice_roller: Dice roller instance (creates new if not provided)
        """
        self.config = config
        self.llm_client = llm_client
        self.session_log = session_log
        self.dice_roller = dice_roller or DiceRoller()
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        """Build the system prompt for the DM agent.

        Returns:
            System prompt string
        """
        return """You are an expert Dungeon Master running a tabletop RPG game.

Your role is to:
- Create engaging narratives and describe the world vividly
- Manage NPCs with distinct personalities and motivations
- Apply game rules fairly and consistently
- Respond to player actions with appropriate consequences
- Maintain narrative pacing and player engagement
- Use your tools to roll dice, manage scenes, and log events

When narrating:
- Be descriptive but concise
- Focus on sensory details (sights, sounds, smells)
- Show consequences of player actions
- Give players clear choices when appropriate
- Maintain tension and drama

When using tools:
- Roll dice for NPCs and environmental effects
- AFTER rolling dice, ALWAYS narrate what happens based on the result:
  * Low rolls (1-7): describe failure, setbacks, or complications
  * Mid rolls (8-14): describe partial success or mixed outcomes
  * High rolls (15+): describe clear success and positive outcomes
- Start new scenes when the location or situation changes significantly
- End scenes with a brief summary when transitioning
- Log important events and state changes

Remember:
- Players have agency - avoid railroading
- NPCs have limited knowledge - they don't know everything you know
- The rules serve the story, not the other way around
- Safety and comfort of players comes first

Be creative, fair, and engaging. Focus on collaborative storytelling."""

    def get_tools(self) -> list[Tool]:
        """Get the list of tools available to the DM agent.

        Returns:
            List of tool definitions
        """
        return [
            Tool(
                type="function",
                function={
                    "name": "roll_dice",
                    "description": "Roll dice using standard notation. After rolling, you MUST narrate what happens based on the result. Supports d20, 2d6+3, 4d6kh3 (keep highest), advantage/disadvantage, and arbitrary dice sizes like d3, d7, d25, d100.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "notation": {
                                "type": "string",
                                "description": "Dice notation (e.g., 'd20', '2d6+3', '4d6kh3', 'd25')",
                            },
                            "roll_type": {
                                "type": "string",
                                "enum": ["normal", "advantage", "disadvantage"],
                                "description": "Type of roll (default: normal)",
                            },
                            "purpose": {
                                "type": "string",
                                "description": "What this roll is for (e.g., 'Goblin attack roll', 'Perception check')",
                            },
                        },
                        "required": ["notation", "purpose"],
                    },
                },
            ),
            Tool(
                type="function",
                function={
                    "name": "start_scene",
                    "description": "Begin a new narrative scene when the location or situation changes significantly. Scenes help organize the story into manageable chunks.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Descriptive title for the scene (e.g., 'The Leaky Dragon Tavern', 'Ambush on the Road')",
                            },
                            "location": {
                                "type": "string",
                                "description": "Where this scene takes place (e.g., 'Tavern', 'Forest Road', 'Castle Throne Room')",
                            },
                        },
                        "required": ["title", "location"],
                    },
                },
            ),
            Tool(
                type="function",
                function={
                    "name": "end_scene",
                    "description": "End the current scene with an optional summary. Use when transitioning to a new location or significant situation change.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "summary": {
                                "type": "string",
                                "description": "Brief summary of what happened in this scene (2-3 sentences)",
                            },
                        },
                        "required": [],
                    },
                },
            ),
            Tool(
                type="function",
                function={
                    "name": "log_event",
                    "description": "Log an important event, state change, or significant moment. Use for tracking key narrative beats, item acquisitions, NPC reactions, or world state changes.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "event_type": {
                                "type": "string",
                                "enum": [
                                    "narration",
                                    "player_action",
                                    "dice_roll",
                                    "npc_action",
                                    "npc_dialogue",
                                    "system",
                                    "tool_call",
                                    "state_change",
                                ],
                                "description": "Type of event being logged",
                            },
                            "content": {
                                "type": "string",
                                "description": "Description of what happened",
                            },
                            "actor": {
                                "type": "string",
                                "description": "Who performed this action (player name, NPC name, or 'system')",
                            },
                        },
                        "required": ["event_type", "content"],
                    },
                },
            ),
        ]

    def _execute_tool(self, tool_name: str, arguments: dict) -> str:
        """Execute a tool call and return the result.

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments

        Returns:
            Tool execution result as string
        """
        if tool_name == "roll_dice":
            notation = arguments["notation"]
            roll_type = arguments.get("roll_type", "normal")
            purpose = arguments["purpose"]

            if roll_type == "advantage":
                result = self.dice_roller.advantage(notation)
            elif roll_type == "disadvantage":
                result = self.dice_roller.disadvantage(notation)
            else:
                result = self.dice_roller.roll(notation)

            # Log the dice roll
            self.session_log.log_event(
                event_type="dice_roll",
                content=f"{purpose}: {result.details}",
                actor="DM",
                metadata={"notation": notation, "roll_type": roll_type, "total": result.total},
            )

            return f"Roll result: {result.details}"

        elif tool_name == "start_scene":
            title = arguments["title"]
            location = arguments["location"]
            scene = self.session_log.start_scene(title=title, location=location)
            return f"Started new scene: '{title}' at {location} (Scene ID: {scene.scene_id})"

        elif tool_name == "end_scene":
            summary = arguments.get("summary")
            self.session_log.end_scene(summary=summary)
            return f"Ended current scene. Summary: {summary if summary else 'None'}"

        elif tool_name == "log_event":
            event_type = arguments["event_type"]
            content = arguments["content"]
            actor = arguments.get("actor", "system")
            self.session_log.log_event(
                event_type=event_type, content=content, actor=actor, metadata={}
            )
            return f"Logged {event_type} event: {content[:50]}..."

        else:
            return f"Unknown tool: {tool_name}"

    def respond(self, player_message: str) -> str:
        """Get DM response to player message (non-streaming).

        Args:
            player_message: Message from the player

        Returns:
            DM's response
        """
        # Log player action
        self.session_log.log_event(
            event_type="player_action", content=player_message, actor="Player", metadata={}
        )

        # Build context from session history
        context = self.session_log.get_context_for_llm(
            include_current_scene_events=True,
            include_previous_scenes=2,
            include_older_summaries=True,
        )

        # Build messages
        messages = [
            ChatMessage(role=ChatRole.SYSTEM, content=self.system_prompt),
            ChatMessage(role=ChatRole.SYSTEM, content=f"Session context:\n{context}"),
            ChatMessage(role=ChatRole.USER, content=player_message),
        ]

        # Get LLM response with tool calling
        response = self.llm_client.chat(
            messages=messages,
            model=self.config.dm_model,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            tools=self.get_tools(),
        )

        # Handle tool calls if present
        while response.tool_calls:
            # Add assistant message with tool calls (convert to dict format)
            tool_calls_dict = [tc.model_dump() for tc in response.tool_calls]
            messages.append(
                ChatMessage(
                    role=ChatRole.ASSISTANT,
                    content=response.content or "",
                    tool_calls=tool_calls_dict,
                )
            )

            # Execute all tool calls and add results
            for tool_call in response.tool_calls:
                result = self._execute_tool(tool_call.function.name, tool_call.function.arguments)

                # Add tool result
                messages.append(
                    ChatMessage(role=ChatRole.TOOL, content=result, tool_call_id=tool_call.id)
                )

            # Get next response
            response = self.llm_client.chat(
                messages=messages,
                model=self.config.dm_model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                tools=self.get_tools(),
            )

        # Log DM narration
        if response.content:
            self.session_log.log_event(
                event_type="narration", content=response.content, actor="DM", metadata={}
            )

        return response.content or ""

    def respond_stream(self, player_message: str) -> Iterator[str]:
        """Get DM response to player message (streaming).

        Args:
            player_message: Message from the player

        Yields:
            Chunks of the DM's response
        """
        # Log player action
        self.session_log.log_event(
            event_type="player_action", content=player_message, actor="Player", metadata={}
        )

        # Build context from session history
        context = self.session_log.get_context_for_llm(
            include_current_scene_events=True,
            include_previous_scenes=2,
            include_older_summaries=True,
        )

        # Build messages
        messages = [
            ChatMessage(role=ChatRole.SYSTEM, content=self.system_prompt),
            ChatMessage(role=ChatRole.SYSTEM, content=f"Session context:\n{context}"),
            ChatMessage(role=ChatRole.USER, content=player_message),
        ]

        # Track accumulated response
        accumulated_content = ""
        accumulated_tool_calls = []

        # Get streaming response
        for chunk in self.llm_client.chat_stream(
            messages=messages,
            model=self.config.dm_model,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            tools=self.get_tools(),
        ):
            if chunk.content:
                accumulated_content += chunk.content
                yield chunk.content

            if chunk.tool_calls:
                accumulated_tool_calls.extend(chunk.tool_calls)

            # Check if stream is done
            if chunk.finish_reason:
                break

        # Handle tool calls if present
        if accumulated_tool_calls:
            # Add assistant message with tool calls (convert to dict format)
            tool_calls_dict = [tc.model_dump() for tc in accumulated_tool_calls]
            messages.append(
                ChatMessage(
                    role=ChatRole.ASSISTANT,
                    content=accumulated_content or None,
                    tool_calls=tool_calls_dict,
                )
            )

            # Execute tool calls and add results
            for tool_call in accumulated_tool_calls:
                result = self._execute_tool(tool_call.function.name, tool_call.function.arguments)
                messages.append(
                    ChatMessage(role=ChatRole.TOOL, content=result, tool_call_id=tool_call.id)
                )
                # Yield tool result to user
                yield f"\n[{tool_call.function.name}: {result}]\n"

            # Get next response after tool calls
            accumulated_content = ""
            for chunk in self.llm_client.chat_stream(
                messages=messages,
                model=self.config.dm_model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                tools=self.get_tools(),
            ):
                if chunk.content:
                    accumulated_content += chunk.content
                    yield chunk.content

        # Log final DM narration
        if accumulated_content:
            self.session_log.log_event(
                event_type="narration", content=accumulated_content, actor="DM", metadata={}
            )
