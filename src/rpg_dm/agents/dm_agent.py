"""DM Agent - Primary orchestrator and world manager."""

from typing import Iterator, Optional

from rpg_dm.campaign import CampaignManager, NPCProfile, Location, PlotThread, PlotStatus
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
        campaign_manager: Optional[CampaignManager] = None,
    ):
        """Initialize DM agent.

        Args:
            config: Application configuration
            llm_client: LLM client for making API calls
            session_log: Session log for memory management
            dice_roller: Dice roller instance (creates new if not provided)
            campaign_manager: Optional campaign manager for multi-session tracking
        """
        self.config = config
        self.llm_client = llm_client
        self.session_log = session_log
        self.dice_roller = dice_roller or DiceRoller()
        self.campaign_manager = campaign_manager
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

Campaign tracking (if available):
- Use track_npc when introducing or updating important NPCs
- Use track_location when visiting significant places
- Use add_plot_thread when a new story arc begins
- Use update_plot_thread when plot developments occur
- Consult campaign context for NPC knowledge and relationships
- Maintain consistency with established locations and events

Remember:
- Players have agency - avoid railroading
- NPCs have limited knowledge - they don't know everything you know as DM
- Track what each NPC knows separately for realistic interactions
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

        # Add campaign tools if campaign manager is available
        if self.campaign_manager:
            campaign_tools = [
                Tool(
                    type="function",
                    function={
                        "name": "track_npc",
                        "description": "Track or update an important NPC in the campaign. Use when introducing a new significant NPC or updating their knowledge/relationships.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "NPC name"},
                                "description": {"type": "string", "description": "Physical appearance and personality"},
                                "role": {
                                    "type": "string",
                                    "description": "NPC's role (e.g., 'quest giver', 'antagonist', 'merchant', 'ally')",
                                },
                                "knowledge": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "What this NPC knows (add new knowledge items)",
                                },
                                "location": {"type": "string", "description": "Where NPC was last seen"},
                            },
                            "required": ["name", "description"],
                        },
                    },
                ),
                Tool(
                    type="function",
                    function={
                        "name": "track_location",
                        "description": "Track or update a location in the campaign. Use when visiting a new important place or when significant events occur at a location.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Location name"},
                                "description": {"type": "string", "description": "Location description"},
                                "event": {
                                    "type": "string",
                                    "description": "Notable event that just happened here",
                                },
                            },
                            "required": ["name", "description"],
                        },
                    },
                ),
                Tool(
                    type="function",
                    function={
                        "name": "add_plot_thread",
                        "description": "Create a new plot thread when a new story arc or quest begins.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string", "description": "Plot thread title"},
                                "description": {"type": "string", "description": "What this plot thread is about"},
                                "related_npcs": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "NPCs involved in this plot",
                                },
                            },
                            "required": ["title", "description"],
                        },
                    },
                ),
                Tool(
                    type="function",
                    function={
                        "name": "update_plot_thread",
                        "description": "Update an existing plot thread when significant developments occur.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string", "description": "Plot thread title to update"},
                                "update": {"type": "string", "description": "What happened in this plot"},
                                "status": {
                                    "type": "string",
                                    "enum": ["active", "completed", "abandoned", "on_hold"],
                                    "description": "Updated status if changed",
                                },
                            },
                            "required": ["title", "update"],
                        },
                    },
                ),
            ]
            return [*campaign_tools, *tools]

        return tools

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

        # Campaign tools
        elif tool_name == "track_npc" and self.campaign_manager:
            name = arguments["name"]
            description = arguments["description"]
            role = arguments.get("role")
            knowledge = arguments.get("knowledge", [])
            location = arguments.get("location")

            # Get existing NPC or create new one
            npc = self.campaign_manager.campaign.get_npc(name)
            if npc:
                # Update existing NPC
                npc.description = description
                if role:
                    npc.role = role
                for k in knowledge:
                    npc.add_knowledge(k)
                if location:
                    npc.last_seen_location = location
                    npc.last_seen_session = self.session_log.session_id
            else:
                # Create new NPC
                npc = NPCProfile(
                    name=name,
                    description=description,
                    role=role,
                    knowledge=knowledge,
                    last_seen_location=location,
                    last_seen_session=self.session_log.session_id,
                    first_appeared_session=self.session_log.session_id,
                )
                self.campaign_manager.campaign.add_npc(npc)
            
            self.campaign_manager.save()
            return f"Tracked NPC '{name}' in campaign"

        elif tool_name == "track_location" and self.campaign_manager:
            name = arguments["name"]
            description = arguments["description"]
            event = arguments.get("event")

            # Get existing location or create new one
            location = self.campaign_manager.campaign.get_location(name)
            if location:
                # Update existing location
                location.description = description
                if event:
                    location.add_event(event)
                location.last_visited_session = self.session_log.session_id
            else:
                # Create new location
                location = Location(
                    name=name,
                    description=description,
                    notable_events=[event] if event else [],
                    first_visited_session=self.session_log.session_id,
                    last_visited_session=self.session_log.session_id,
                )
                self.campaign_manager.campaign.add_location(location)
            
            self.campaign_manager.save()
            return f"Tracked location '{name}' in campaign"

        elif tool_name == "add_plot_thread" and self.campaign_manager:
            title = arguments["title"]
            description = arguments["description"]
            related_npcs = arguments.get("related_npcs", [])

            # Generate plot thread ID
            plot_count = len(self.campaign_manager.campaign.plot_threads)
            plot_id = f"plot_{plot_count + 1:03d}"

            plot_thread = PlotThread(
                id=plot_id,
                title=title,
                description=description,
                status=PlotStatus.ACTIVE,
                related_npcs=related_npcs,
                created_in_session=self.session_log.session_id,
            )
            self.campaign_manager.campaign.add_plot_thread(plot_thread)
            self.campaign_manager.save()
            return f"Added new plot thread: '{title}'"

        elif tool_name == "update_plot_thread" and self.campaign_manager:
            title = arguments["title"]
            update = arguments["update"]
            status = arguments.get("status")

            # Find plot thread by title
            plot_thread = next(
                (pt for pt in self.campaign_manager.campaign.plot_threads if pt.title == title),
                None
            )
            
            if plot_thread:
                plot_thread.add_update(
                    session_id=self.session_log.session_id,
                    description=update,
                )
                if status:
                    plot_thread.status = PlotStatus(status)
                self.campaign_manager.save()
                return f"Updated plot thread '{title}': {update}"
            else:
                return f"Plot thread '{title}' not found"

        else:
            return f"Unknown tool: {tool_name}"

    def _get_campaign_context(self) -> str:
        """Get campaign context for the LLM.

        Returns:
            Formatted campaign context string
        """
        if not self.campaign_manager or not self.campaign_manager.campaign:
            return ""

        campaign = self.campaign_manager.campaign
        context_parts = []

        # Campaign overview
        context_parts.append(f"Campaign: {campaign.name}")
        context_parts.append(f"Setting: {campaign.setting}")
        if campaign.overarching_goal:
            context_parts.append(f"Overarching Goal: {campaign.overarching_goal}")
        context_parts.append("")

        # Active plot threads
        active_plots = campaign.get_plot_threads_by_status(PlotStatus.ACTIVE)
        if active_plots:
            context_parts.append("Active Plot Threads:")
            for plot in active_plots:
                context_parts.append(f"- {plot.title}: {plot.description}")
                if plot.updates:
                    latest = plot.updates[-1]
                    context_parts.append(f"  Latest: {latest.description}")
            context_parts.append("")

        # Known NPCs (limit to most relevant)
        if campaign.npcs:
            context_parts.append("Known NPCs:")
            for name, npc in list(campaign.npcs.items())[:10]:  # Limit to 10 most recent
                context_parts.append(f"- {name} ({npc.role or 'NPC'}): {npc.description}")
                if npc.knowledge:
                    context_parts.append(f"  Knows: {', '.join(npc.knowledge[:3])}")
                if npc.last_seen_location:
                    context_parts.append(f"  Last seen: {npc.last_seen_location}")
            context_parts.append("")

        # Known locations (limit to most relevant)
        if campaign.locations:
            context_parts.append("Known Locations:")
            for name, loc in list(campaign.locations.items())[:8]:  # Limit to 8
                context_parts.append(f"- {name}: {loc.description[:100]}")
                if loc.notable_events:
                    context_parts.append(f"  Events: {loc.notable_events[-1]}")
            context_parts.append("")

        return "\n".join(context_parts)

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
        ]
        
        # Add campaign context if available
        campaign_context = self._get_campaign_context()
        if campaign_context:
            messages.append(
                ChatMessage(role=ChatRole.SYSTEM, content=f"Campaign Context:\n{campaign_context}")
            )
        
        # Add session context
        messages.append(
            ChatMessage(role=ChatRole.SYSTEM, content=f"Session context:\n{context}")
        )
        messages.append(
            ChatMessage(role=ChatRole.USER, content=player_message)
        )

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
