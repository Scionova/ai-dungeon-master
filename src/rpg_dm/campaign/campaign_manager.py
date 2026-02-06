"""Campaign manager for loading, saving, and managing campaigns."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from ..config import get_config
from .models import Campaign, Location, NPCProfile, PlotStatus, PlotThread


class CampaignManager:
    """Manages campaign persistence and operations."""

    def __init__(self, campaign_id: Optional[str] = None):
        """Initialize campaign manager.

        Args:
            campaign_id: Unique identifier for the campaign. If None, generates from timestamp.
        """
        self.campaign_id = campaign_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.config = get_config()
        self.campaign: Optional[Campaign] = None

        # Create campaigns directory
        self.campaigns_dir = self.config.data_dir / "campaigns"
        self.campaigns_dir.mkdir(parents=True, exist_ok=True)

        # Templates directory
        self.templates_dir = self.config.data_dir / "campaign_templates"
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        # Campaign file path
        self.campaign_file = self.campaigns_dir / f"{self.campaign_id}.json"

    def create_campaign(
        self,
        name: str,
        setting: str,
        overarching_goal: Optional[str] = None,
    ) -> Campaign:
        """Create a new campaign.

        Args:
            name: Campaign name
            setting: Campaign setting description
            overarching_goal: Optional main quest or goal

        Returns:
            Created campaign
        """
        self.campaign = Campaign(
            campaign_id=self.campaign_id,
            name=name,
            setting=setting,
            overarching_goal=overarching_goal,
        )
        self.save()
        return self.campaign

    def load_from_template(self, template_path: Path) -> Campaign:
        """Load a campaign from a template file.

        Args:
            template_path: Path to the template JSON file

        Returns:
            Campaign created from template

        Raises:
            FileNotFoundError: If template file doesn't exist
            ValueError: If template is invalid
        """
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        with open(template_path) as f:
            template_data = json.load(f)

        # Create base campaign
        self.campaign = Campaign(
            campaign_id=self.campaign_id,
            name=template_data["name"],
            setting=template_data["setting"],
            overarching_goal=template_data.get("overarching_goal"),
            metadata=template_data.get("metadata", {}),
        )

        # Load NPCs
        for npc_name, npc_data in template_data.get("npcs", {}).items():
            npc = NPCProfile(
                name=npc_name,
                description=npc_data["description"],
                role=npc_data.get("role"),
                knowledge=npc_data.get("knowledge", []),
                relationships=npc_data.get("relationships", {}),
                notes=npc_data.get("notes", []),
            )
            self.campaign.add_npc(npc)

        # Load locations
        for loc_name, loc_data in template_data.get("locations", {}).items():
            location = Location(
                name=loc_name,
                description=loc_data["description"],
                notable_events=loc_data.get("notable_events", []),
                npcs_present=loc_data.get("npcs_present", []),
                notes=loc_data.get("notes", []),
            )
            self.campaign.add_location(location)

        # Load plot threads
        for idx, pt_data in enumerate(template_data.get("plot_threads", [])):
            # Generate ID from index
            thread_id = f"plot_{idx + 1:03d}"
            plot_thread = PlotThread(
                id=thread_id,
                title=pt_data["title"],
                description=pt_data["description"],
                status=PlotStatus(pt_data.get("status", "active")),
                related_npcs=pt_data.get("related_npcs", []),
                related_locations=pt_data.get("related_locations", []),
                created_in_session="template",  # Mark as from template
            )
            self.campaign.add_plot_thread(plot_thread)

        self.save()
        return self.campaign

    def load(self) -> Campaign:
        """Load campaign from disk.

        Returns:
            Loaded campaign

        Raises:
            FileNotFoundError: If campaign file doesn't exist
        """
        if not self.campaign_file.exists():
            raise FileNotFoundError(f"Campaign file not found: {self.campaign_file}")

        with open(self.campaign_file) as f:
            data = json.load(f)

        self.campaign = Campaign.from_dict(data)
        return self.campaign

    def save(self) -> None:
        """Save campaign to disk.

        Raises:
            ValueError: If no campaign is loaded
        """
        if not self.campaign:
            raise ValueError("No campaign loaded to save")

        data = self.campaign.to_dict()

        with open(self.campaign_file, "w") as f:
            json.dump(data, f, indent=2)

    def get_summary(self) -> dict[str, Any]:
        """Get summary of campaign.

        Returns:
            Dictionary with campaign summary

        Raises:
            ValueError: If no campaign is loaded
        """
        if not self.campaign:
            raise ValueError("No campaign loaded")

        active_plots = self.campaign.get_plot_threads_by_status(PlotStatus.ACTIVE)
        completed_plots = self.campaign.get_plot_threads_by_status(PlotStatus.COMPLETED)

        return {
            "campaign_id": self.campaign.campaign_id,
            "name": self.campaign.name,
            "setting": self.campaign.setting,
            "overarching_goal": self.campaign.overarching_goal,
            "start_date": self.campaign.start_date.isoformat(),
            "npc_count": len(self.campaign.npcs),
            "location_count": len(self.campaign.locations),
            "active_plot_count": len(active_plots),
            "completed_plot_count": len(completed_plots),
            "session_count": len(self.campaign.sessions),
            "sessions": self.campaign.sessions,
        }

    @staticmethod
    def list_campaigns(data_dir: Optional[Path] = None) -> list[dict[str, str]]:
        """List all available campaigns.

        Args:
            data_dir: Optional data directory path

        Returns:
            List of campaign info dicts with id, name, start_date
        """
        if data_dir is None:
            data_dir = get_config().data_dir

        campaigns_dir = data_dir / "campaigns"
        if not campaigns_dir.exists():
            return []

        campaigns = []
        for campaign_file in sorted(campaigns_dir.glob("*.json"), reverse=True):
            try:
                with open(campaign_file) as f:
                    data = json.load(f)
                campaigns.append({
                    "id": data["campaign_id"],
                    "name": data["name"],
                    "start_date": data["start_date"],
                    "sessions": len(data.get("sessions", [])),
                })
            except (json.JSONDecodeError, KeyError):
                continue

        return campaigns

    @staticmethod
    def list_templates(data_dir: Optional[Path] = None) -> list[dict[str, str]]:
        """List all available campaign templates.

        Args:
            data_dir: Optional data directory path

        Returns:
            List of template info dicts with filename and name
        """
        if data_dir is None:
            data_dir = get_config().data_dir

        templates_dir = data_dir / "campaign_templates"
        if not templates_dir.exists():
            return []

        templates = []
        for template_file in sorted(templates_dir.glob("*.json")):
            # Skip README and blank template
            if template_file.stem in ["template_blank", "README"]:
                continue

            try:
                with open(template_file) as f:
                    data = json.load(f)
                templates.append({
                    "filename": template_file.name,
                    "path": str(template_file),
                    "name": data.get("name", template_file.stem),
                    "setting": data.get("setting", "")[:100],  # First 100 chars
                })
            except (json.JSONDecodeError, KeyError):
                continue

        return templates
