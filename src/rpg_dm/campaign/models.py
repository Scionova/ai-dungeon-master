"""Data models for campaign tracking across multiple sessions."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class PlotStatus(str, Enum):
    """Status of a plot thread."""

    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    ON_HOLD = "on_hold"


class PlotUpdate(BaseModel):
    """An update to a plot thread."""

    timestamp: datetime = Field(default_factory=datetime.now)
    session_id: str
    description: str
    metadata: dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert plot update to dictionary for serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "session_id": self.session_id,
            "description": self.description,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PlotUpdate":
        """Create plot update from dictionary."""
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            session_id=data["session_id"],
            description=data["description"],
            metadata=data.get("metadata", {}),
        )


class PlotThread(BaseModel):
    """A plot thread or story arc within the campaign."""

    id: str
    title: str
    description: str
    status: PlotStatus = PlotStatus.ACTIVE
    related_npcs: list[str] = Field(default_factory=list)
    related_locations: list[str] = Field(default_factory=list)
    created_in_session: str
    created_at: datetime = Field(default_factory=datetime.now)
    updates: list[PlotUpdate] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def add_update(self, session_id: str, description: str, metadata: Optional[dict[str, Any]] = None) -> None:
        """Add an update to this plot thread.

        Args:
            session_id: Session where update occurred
            description: Description of the update
            metadata: Optional additional metadata
        """
        update = PlotUpdate(
            session_id=session_id,
            description=description,
            metadata=metadata or {},
        )
        self.updates.append(update)

    def to_dict(self) -> dict[str, Any]:
        """Convert plot thread to dictionary for serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "related_npcs": self.related_npcs,
            "related_locations": self.related_locations,
            "created_in_session": self.created_in_session,
            "created_at": self.created_at.isoformat(),
            "updates": [update.to_dict() for update in self.updates],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PlotThread":
        """Create plot thread from dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            status=PlotStatus(data["status"]),
            related_npcs=data.get("related_npcs", []),
            related_locations=data.get("related_locations", []),
            created_in_session=data["created_in_session"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updates=[PlotUpdate.from_dict(u) for u in data.get("updates", [])],
            metadata=data.get("metadata", {}),
        )


class NPCProfile(BaseModel):
    """Profile for a persistent NPC in the campaign."""

    name: str
    description: str
    role: Optional[str] = None  # e.g., "quest giver", "antagonist", "merchant"
    knowledge: list[str] = Field(default_factory=list)  # What the NPC knows
    relationships: dict[str, str] = Field(default_factory=dict)  # name -> relationship description
    last_seen_location: Optional[str] = None
    last_seen_session: Optional[str] = None
    first_appeared_session: Optional[str] = None
    notes: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def add_knowledge(self, knowledge_item: str) -> None:
        """Add something the NPC knows.

        Args:
            knowledge_item: Knowledge to add
        """
        if knowledge_item not in self.knowledge:
            self.knowledge.append(knowledge_item)

    def set_relationship(self, target_name: str, relationship: str) -> None:
        """Set or update relationship with another character.

        Args:
            target_name: Name of the other character
            relationship: Description of the relationship
        """
        self.relationships[target_name] = relationship

    def add_note(self, note: str) -> None:
        """Add a note about the NPC.

        Args:
            note: Note to add
        """
        self.notes.append(note)

    def to_dict(self) -> dict[str, Any]:
        """Convert NPC profile to dictionary for serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "role": self.role,
            "knowledge": self.knowledge,
            "relationships": self.relationships,
            "last_seen_location": self.last_seen_location,
            "last_seen_session": self.last_seen_session,
            "first_appeared_session": self.first_appeared_session,
            "notes": self.notes,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "NPCProfile":
        """Create NPC profile from dictionary."""
        return cls(
            name=data["name"],
            description=data["description"],
            role=data.get("role"),
            knowledge=data.get("knowledge", []),
            relationships=data.get("relationships", {}),
            last_seen_location=data.get("last_seen_location"),
            last_seen_session=data.get("last_seen_session"),
            first_appeared_session=data.get("first_appeared_session"),
            notes=data.get("notes", []),
            metadata=data.get("metadata", {}),
        )


class Location(BaseModel):
    """A location in the campaign world."""

    name: str
    description: str
    notable_events: list[str] = Field(default_factory=list)  # Key events that happened here
    npcs_present: list[str] = Field(default_factory=list)  # Names of NPCs currently here
    first_visited_session: Optional[str] = None
    last_visited_session: Optional[str] = None
    notes: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def add_event(self, event_description: str) -> None:
        """Add a notable event that occurred at this location.

        Args:
            event_description: Description of the event
        """
        self.notable_events.append(event_description)

    def add_npc(self, npc_name: str) -> None:
        """Add an NPC to this location.

        Args:
            npc_name: Name of the NPC
        """
        if npc_name not in self.npcs_present:
            self.npcs_present.append(npc_name)

    def remove_npc(self, npc_name: str) -> bool:
        """Remove an NPC from this location.

        Args:
            npc_name: Name of the NPC

        Returns:
            True if removed, False if not found
        """
        if npc_name in self.npcs_present:
            self.npcs_present.remove(npc_name)
            return True
        return False

    def add_note(self, note: str) -> None:
        """Add a note about the location.

        Args:
            note: Note to add
        """
        self.notes.append(note)

    def to_dict(self) -> dict[str, Any]:
        """Convert location to dictionary for serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "notable_events": self.notable_events,
            "npcs_present": self.npcs_present,
            "first_visited_session": self.first_visited_session,
            "last_visited_session": self.last_visited_session,
            "notes": self.notes,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Location":
        """Create location from dictionary."""
        return cls(
            name=data["name"],
            description=data["description"],
            notable_events=data.get("notable_events", []),
            npcs_present=data.get("npcs_present", []),
            first_visited_session=data.get("first_visited_session"),
            last_visited_session=data.get("last_visited_session"),
            notes=data.get("notes", []),
            metadata=data.get("metadata", {}),
        )


class Campaign(BaseModel):
    """A campaign containing multiple sessions with persistent world state."""

    campaign_id: str
    name: str
    setting: str  # Description of the campaign setting
    overarching_goal: Optional[str] = None  # Main quest or purpose
    start_date: datetime = Field(default_factory=datetime.now)
    npcs: dict[str, NPCProfile] = Field(default_factory=dict)  # name -> profile
    locations: dict[str, Location] = Field(default_factory=dict)  # name -> location
    plot_threads: list[PlotThread] = Field(default_factory=list)
    sessions: list[str] = Field(default_factory=list)  # Chronological session IDs
    metadata: dict[str, Any] = Field(default_factory=dict)

    def add_npc(self, npc: NPCProfile) -> None:
        """Add or update an NPC in the campaign.

        Args:
            npc: NPC profile to add
        """
        self.npcs[npc.name] = npc

    def get_npc(self, name: str) -> Optional[NPCProfile]:
        """Get an NPC by name.

        Args:
            name: NPC name

        Returns:
            NPC profile or None if not found
        """
        return self.npcs.get(name)

    def add_location(self, location: Location) -> None:
        """Add or update a location in the campaign.

        Args:
            location: Location to add
        """
        self.locations[location.name] = location

    def get_location(self, name: str) -> Optional[Location]:
        """Get a location by name.

        Args:
            name: Location name

        Returns:
            Location or None if not found
        """
        return self.locations.get(name)

    def add_plot_thread(self, plot_thread: PlotThread) -> None:
        """Add a new plot thread to the campaign.

        Args:
            plot_thread: Plot thread to add
        """
        self.plot_threads.append(plot_thread)

    def get_plot_thread(self, thread_id: str) -> Optional[PlotThread]:
        """Get a plot thread by ID.

        Args:
            thread_id: Plot thread ID

        Returns:
            Plot thread or None if not found
        """
        return next((pt for pt in self.plot_threads if pt.id == thread_id), None)

    def get_plot_threads_by_status(self, status: PlotStatus) -> list[PlotThread]:
        """Get all plot threads with a specific status.

        Args:
            status: Status to filter by

        Returns:
            List of matching plot threads
        """
        return [pt for pt in self.plot_threads if pt.status == status]

    def add_session(self, session_id: str) -> None:
        """Link a session to this campaign.

        Args:
            session_id: Session ID to add
        """
        if session_id not in self.sessions:
            self.sessions.append(session_id)

    def to_dict(self) -> dict[str, Any]:
        """Convert campaign to dictionary for serialization."""
        return {
            "campaign_id": self.campaign_id,
            "name": self.name,
            "setting": self.setting,
            "overarching_goal": self.overarching_goal,
            "start_date": self.start_date.isoformat(),
            "npcs": {name: npc.to_dict() for name, npc in self.npcs.items()},
            "locations": {name: loc.to_dict() for name, loc in self.locations.items()},
            "plot_threads": [pt.to_dict() for pt in self.plot_threads],
            "sessions": self.sessions,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Campaign":
        """Create campaign from dictionary."""
        return cls(
            campaign_id=data["campaign_id"],
            name=data["name"],
            setting=data["setting"],
            overarching_goal=data.get("overarching_goal"),
            start_date=datetime.fromisoformat(data["start_date"]),
            npcs={name: NPCProfile.from_dict(npc_data) for name, npc_data in data.get("npcs", {}).items()},
            locations={name: Location.from_dict(loc_data) for name, loc_data in data.get("locations", {}).items()},
            plot_threads=[PlotThread.from_dict(pt_data) for pt_data in data.get("plot_threads", [])],
            sessions=data.get("sessions", []),
            metadata=data.get("metadata", {}),
        )
