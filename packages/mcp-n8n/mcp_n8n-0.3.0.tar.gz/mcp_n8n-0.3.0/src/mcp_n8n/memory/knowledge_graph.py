"""Knowledge graph for agent learning and note-linking.

Implements Zettelkasten-inspired knowledge management with:
- Individual markdown notes with YAML frontmatter
- Bidirectional linking between notes
- Tag-based organization
- Confidence tracking
"""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal


class KnowledgeGraph:
    """Knowledge graph storage and query interface."""

    def __init__(self, base_dir: Path | None = None) -> None:
        """Initialize knowledge graph.

        Args:
            base_dir: Base directory for knowledge storage
        """
        self.base_dir = base_dir or Path(".chora/memory/knowledge")
        self.notes_dir = self.base_dir / "notes"
        self.notes_dir.mkdir(parents=True, exist_ok=True)

        self.links_file = self.base_dir / "links.json"
        self.tags_file = self.base_dir / "tags.json"

    def create_note(
        self,
        title: str,
        content: str,
        tags: list[str] | None = None,
        links: list[str] | None = None,
        confidence: Literal["low", "medium", "high"] = "medium",
        source: str = "agent-learning",
    ) -> str:
        """Create new knowledge note.

        Args:
            title: Note title
            content: Note content (markdown)
            tags: List of tags
            links: List of note IDs to link to
            confidence: Confidence level
            source: Source of knowledge

        Returns:
            Note ID
        """
        # Generate note ID from title
        note_id = title.lower().replace(" ", "-").replace("/", "-")
        note_file = self.notes_dir / f"{note_id}.md"

        # Prevent overwriting existing notes
        if note_file.exists():
            raise ValueError(f"Note '{note_id}' already exists")

        # Create frontmatter
        now = datetime.now(UTC).isoformat()
        frontmatter = {
            "id": note_id,
            "created": now,
            "updated": now,
            "tags": tags or [],
            "confidence": confidence,
            "source": source,
            "linked_to": links or [],
        }

        # Write note
        with note_file.open("w", encoding="utf-8") as f:
            f.write("---\n")
            for key, value in frontmatter.items():
                if isinstance(value, list):
                    f.write(f"{key}: {json.dumps(value)}\n")
                else:
                    f.write(f"{key}: {value}\n")
            f.write("---\n\n")
            f.write(f"# {title}\n\n")
            f.write(content)

        # Update links graph
        if links:
            self._update_links(note_id, links, operation="add")

        # Update tags index
        if tags:
            self._update_tags(note_id, tags, operation="add")

        return note_id

    def update_note(
        self,
        note_id: str,
        content_append: str | None = None,
        links_add: list[str] | None = None,
        tags_add: list[str] | None = None,
    ) -> None:
        """Update existing knowledge note.

        Args:
            note_id: Note ID
            content_append: Content to append
            links_add: Links to add
            tags_add: Tags to add
        """
        note_file = self.notes_dir / f"{note_id}.md"
        if not note_file.exists():
            raise ValueError(f"Note '{note_id}' not found")

        # Read existing note
        with note_file.open("r", encoding="utf-8") as f:
            content = f.read()

        # Parse frontmatter
        frontmatter_end = content.find("---\n", 4)
        frontmatter_text = content[4:frontmatter_end]
        note_content = content[frontmatter_end + 4 :]

        # Parse frontmatter fields
        frontmatter: dict[str, Any] = {}
        for line in frontmatter_text.strip().split("\n"):
            if ": " not in line:
                continue
            key, value = line.split(": ", 1)
            if value.startswith("["):
                frontmatter[key] = json.loads(value)
            else:
                frontmatter[key] = value

        # Update timestamp
        frontmatter["updated"] = datetime.now(UTC).isoformat()

        # Update links
        if links_add:
            existing_links = frontmatter.get("linked_to", [])
            new_links = list(set(existing_links + links_add))
            frontmatter["linked_to"] = new_links
            self._update_links(note_id, links_add, operation="add")

        # Update tags
        if tags_add:
            existing_tags = frontmatter.get("tags", [])
            new_tags = list(set(existing_tags + tags_add))
            frontmatter["tags"] = new_tags
            self._update_tags(note_id, tags_add, operation="add")

        # Append content
        if content_append:
            note_content += "\n\n" + content_append

        # Write updated note
        with note_file.open("w", encoding="utf-8") as f:
            f.write("---\n")
            for key, value in frontmatter.items():
                if isinstance(value, list):
                    f.write(f"{key}: {json.dumps(value)}\n")
                else:
                    f.write(f"{key}: {value}\n")
            f.write("---\n")
            f.write(note_content)

    def get_note(self, note_id: str) -> dict[str, Any]:
        """Get knowledge note by ID.

        Args:
            note_id: Note ID

        Returns:
            Note metadata and content
        """
        note_file = self.notes_dir / f"{note_id}.md"
        if not note_file.exists():
            raise ValueError(f"Note '{note_id}' not found")

        with note_file.open("r", encoding="utf-8") as f:
            content = f.read()

        # Parse frontmatter
        frontmatter_end = content.find("---\n", 4)
        frontmatter_text = content[4:frontmatter_end]
        note_content = content[frontmatter_end + 4 :]

        frontmatter: dict[str, Any] = {}
        for line in frontmatter_text.strip().split("\n"):
            if ": " not in line:
                continue
            key, value = line.split(": ", 1)
            if value.startswith("["):
                frontmatter[key] = json.loads(value)
            else:
                frontmatter[key] = value

        return {**frontmatter, "content": note_content}

    def search(
        self,
        tags: list[str] | None = None,
        text: str | None = None,
        confidence: Literal["low", "medium", "high"] | None = None,
    ) -> list[str]:
        """Search for knowledge notes.

        Args:
            tags: Filter by tags (AND condition)
            text: Search in content (case-insensitive)
            confidence: Filter by confidence level

        Returns:
            List of note IDs
        """
        results = []

        for note_file in self.notes_dir.glob("*.md"):
            note_id = note_file.stem
            note = self.get_note(note_id)

            # Filter by tags
            if tags:
                note_tags = set(note.get("tags", []))
                if not all(tag in note_tags for tag in tags):
                    continue

            # Filter by confidence
            if confidence and note.get("confidence") != confidence:
                continue

            # Filter by text
            if text:
                content = note.get("content", "").lower()
                if text.lower() not in content:
                    continue

            results.append(note_id)

        return results

    def get_related(self, note_id: str, max_distance: int = 1) -> list[dict[str, Any]]:
        """Get related notes (linked notes and their links).

        Args:
            note_id: Starting note ID
            max_distance: Maximum link distance (1 = direct links, 2 = links of links)

        Returns:
            List of related notes with distance
        """
        visited: set[str] = {note_id}
        results: list[dict[str, Any]] = []
        current_level = [note_id]

        for distance in range(1, max_distance + 1):
            next_level = []

            for current_id in current_level:
                note = self.get_note(current_id)
                linked = note.get("linked_to", [])

                for linked_id in linked:
                    if linked_id not in visited:
                        visited.add(linked_id)
                        next_level.append(linked_id)
                        results.append({"note_id": linked_id, "distance": distance})

            current_level = next_level

        return results

    def _update_links(
        self, note_id: str, links: list[str], operation: Literal["add", "remove"]
    ) -> None:
        """Update links graph.

        Args:
            note_id: Source note ID
            links: Target note IDs
            operation: "add" or "remove"
        """
        # Load existing links
        if self.links_file.exists():
            with self.links_file.open("r", encoding="utf-8") as f:
                links_data = json.load(f)
        else:
            links_data = {"notes": []}

        # Find or create note entry
        note_entry = next((n for n in links_data["notes"] if n["id"] == note_id), None)
        if not note_entry:
            note_entry = {"id": note_id, "outgoing_links": [], "incoming_links": []}
            links_data["notes"].append(note_entry)

        # Update outgoing links
        if operation == "add":
            note_entry["outgoing_links"] = list(
                set(note_entry.get("outgoing_links", []) + links)
            )
        else:  # remove
            note_entry["outgoing_links"] = [
                link
                for link in note_entry.get("outgoing_links", [])
                if link not in links
            ]

        # Update incoming links for targets
        for target_id in links:
            target_entry = next(
                (n for n in links_data["notes"] if n["id"] == target_id), None
            )
            if not target_entry:
                target_entry = {
                    "id": target_id,
                    "outgoing_links": [],
                    "incoming_links": [],
                }
                links_data["notes"].append(target_entry)

            if operation == "add":
                target_entry["incoming_links"] = list(
                    set(target_entry.get("incoming_links", []) + [note_id])
                )
            else:  # remove
                target_entry["incoming_links"] = [
                    link
                    for link in target_entry.get("incoming_links", [])
                    if link != note_id
                ]

        # Save links
        with self.links_file.open("w", encoding="utf-8") as f:
            json.dump(links_data, f, indent=2)

    def _update_tags(
        self, note_id: str, tags: list[str], operation: Literal["add", "remove"]
    ) -> None:
        """Update tags index.

        Args:
            note_id: Note ID
            tags: Tags to add/remove
            operation: "add" or "remove"
        """
        # Load existing tags
        if self.tags_file.exists():
            with self.tags_file.open("r", encoding="utf-8") as f:
                tags_data = json.load(f)
        else:
            tags_data = {}

        # Update tags
        for tag in tags:
            if tag not in tags_data:
                tags_data[tag] = []

            if operation == "add":
                if note_id not in tags_data[tag]:
                    tags_data[tag].append(note_id)
            else:  # remove
                if note_id in tags_data[tag]:
                    tags_data[tag].remove(note_id)

        # Save tags
        with self.tags_file.open("w", encoding="utf-8") as f:
            json.dump(tags_data, f, indent=2)
