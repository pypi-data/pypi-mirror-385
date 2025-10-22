"""Agent profile management for tracking agent capabilities and preferences."""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class AgentProfile:
    """Agent profile with capabilities, preferences, and learning history."""

    def __init__(
        self,
        agent_name: str,
        agent_version: str = "unknown",
        session_count: int = 0,
        capabilities: dict[str, Any] | None = None,
        preferences: dict[str, Any] | None = None,
        last_active: str | None = None,
    ) -> None:
        """Initialize agent profile.

        Args:
            agent_name: Agent identifier
            agent_version: Agent version string
            session_count: Number of sessions
            capabilities: Capability tracking dictionary
            preferences: Agent preferences
            last_active: ISO timestamp of last activity
        """
        self.agent_name = agent_name
        self.agent_version = agent_version
        self.session_count = session_count
        self.capabilities = capabilities or {}
        self.preferences = preferences or {}
        self.last_active = last_active or datetime.now(UTC).isoformat()

    def to_dict(self) -> dict[str, Any]:
        """Convert profile to dictionary."""
        return {
            "agent_name": self.agent_name,
            "agent_version": self.agent_version,
            "last_active": self.last_active,
            "session_count": self.session_count,
            "capabilities": self.capabilities,
            "preferences": self.preferences,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentProfile":
        """Create profile from dictionary."""
        return cls(
            agent_name=data["agent_name"],
            agent_version=data.get("agent_version", "unknown"),
            session_count=data.get("session_count", 0),
            capabilities=data.get("capabilities", {}),
            preferences=data.get("preferences", {}),
            last_active=data.get("last_active"),
        )

    def update_capability(
        self,
        capability: str,
        skill_level: str | None = None,
        successful_operation: bool | None = None,
        learned_pattern: str | None = None,
    ) -> None:
        """Update capability tracking.

        Args:
            capability: Capability name (e.g., "backend_management")
            skill_level: Skill level ("novice", "intermediate", "expert")
            successful_operation: Whether operation succeeded
            learned_pattern: ID of learned pattern note
        """
        if capability not in self.capabilities:
            self.capabilities[capability] = {
                "skill_level": "novice",
                "successful_operations": 0,
                "failed_operations": 0,
                "learned_patterns": [],
            }

        cap = self.capabilities[capability]

        if skill_level:
            cap["skill_level"] = skill_level

        if successful_operation is not None:
            if successful_operation:
                cap["successful_operations"] = cap.get("successful_operations", 0) + 1
            else:
                cap["failed_operations"] = cap.get("failed_operations", 0) + 1

        if learned_pattern:
            if "learned_patterns" not in cap:
                cap["learned_patterns"] = []
            if learned_pattern not in cap["learned_patterns"]:
                cap["learned_patterns"].append(learned_pattern)

    def set_preference(self, key: str, value: Any) -> None:
        """Set agent preference.

        Args:
            key: Preference key
            value: Preference value
        """
        self.preferences[key] = value

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get agent preference.

        Args:
            key: Preference key
            default: Default value if not set

        Returns:
            Preference value or default
        """
        return self.preferences.get(key, default)

    def increment_session(self) -> None:
        """Increment session count and update last active."""
        self.session_count += 1
        self.last_active = datetime.now(UTC).isoformat()


class AgentProfileManager:
    """Manager for agent profiles."""

    def __init__(self, base_dir: Path | None = None) -> None:
        """Initialize profile manager.

        Args:
            base_dir: Base directory for profiles
                (defaults to .chora/memory/profiles)
        """
        self.base_dir = base_dir or Path(".chora/memory/profiles")
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def get_profile(self, agent_name: str) -> AgentProfile:
        """Get agent profile by name.

        Args:
            agent_name: Agent identifier

        Returns:
            Agent profile

        Raises:
            ValueError: If profile not found
        """
        profile_file = self.base_dir / f"{agent_name}.json"

        if not profile_file.exists():
            raise ValueError(f"Profile not found: {agent_name}")

        with profile_file.open(encoding="utf-8") as f:
            data = json.load(f)

        return AgentProfile.from_dict(data)

    def create_profile(
        self, agent_name: str, agent_version: str = "unknown"
    ) -> AgentProfile:
        """Create new agent profile.

        Args:
            agent_name: Agent identifier
            agent_version: Agent version string

        Returns:
            New agent profile

        Raises:
            ValueError: If profile already exists
        """
        profile_file = self.base_dir / f"{agent_name}.json"

        if profile_file.exists():
            raise ValueError(f"Profile already exists: {agent_name}")

        profile = AgentProfile(agent_name=agent_name, agent_version=agent_version)
        self.save_profile(profile)

        return profile

    def save_profile(self, profile: AgentProfile) -> None:
        """Save agent profile.

        Args:
            profile: Agent profile to save
        """
        profile_file = self.base_dir / f"{profile.agent_name}.json"

        with profile_file.open("w", encoding="utf-8") as f:
            json.dump(profile.to_dict(), f, indent=2)

    def list_profiles(self) -> list[str]:
        """List all agent profiles.

        Returns:
            List of agent names
        """
        return [f.stem for f in self.base_dir.glob("*.json")]

    def get_or_create_profile(
        self, agent_name: str, agent_version: str = "unknown"
    ) -> AgentProfile:
        """Get existing profile or create new one.

        Args:
            agent_name: Agent identifier
            agent_version: Agent version string

        Returns:
            Agent profile
        """
        try:
            return self.get_profile(agent_name)
        except ValueError:
            return self.create_profile(agent_name, agent_version)
