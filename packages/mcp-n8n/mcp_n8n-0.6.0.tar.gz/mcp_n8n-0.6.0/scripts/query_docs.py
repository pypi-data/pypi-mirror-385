#!/usr/bin/env python3
"""
Query documentation for AI agents and humans.

Provides multiple search methods:
- Full-text search across all docs
- Tag-based filtering
- Type-based filtering
- Graph traversal (find related docs)

Output: JSON format for machine consumption
"""

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install PyYAML")
    sys.exit(1)


class DocumentationQuery:
    """Query documentation files with multiple search methods."""

    # Directories to search
    DOC_DIRS = ["docs", "dev-docs"]

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.docs: dict[Path, dict] = {}  # path -> {frontmatter, content}

    def run(self, args: argparse.Namespace) -> None:
        """Execute query based on command-line arguments."""
        # Parse all documentation
        self._parse_all_docs()

        if not self.docs:
            self._output({"error": "No documentation files found", "results": []})
            return

        # Execute query
        if args.topic:
            results = self._search_by_topic(args.topic, args.type)
        elif args.tag:
            results = self._filter_by_tags(args.tag)
        elif args.type:
            results = self._filter_by_type(args.type)
        elif args.related:
            results = self._find_related(args.related)
        else:
            results = list(self.docs.keys())

        # Format results
        formatted = self._format_results(results, args.format)
        self._output(formatted)

    def _parse_all_docs(self) -> None:
        """Parse all markdown files in documentation directories."""
        for doc_dir in self.DOC_DIRS:
            dir_path = self.root_dir / doc_dir
            if not dir_path.exists():
                continue

            for md_file in dir_path.rglob("*.md"):
                fm, content = self._parse_doc(md_file)
                if fm is not None:
                    self.docs[md_file] = {"frontmatter": fm, "content": content}

    def _parse_doc(self, md_file: Path) -> tuple[dict, str]:
        """Parse document frontmatter and content."""
        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception:
            return {}, ""

        # Parse frontmatter
        match = re.match(r"^---\n(.*?)\n---\n(.*)$", content, re.DOTALL)
        if not match:
            return {}, content  # No frontmatter

        try:
            frontmatter = yaml.safe_load(match.group(1))
            if not isinstance(frontmatter, dict):
                frontmatter = {}
        except yaml.YAMLError:
            frontmatter = {}

        doc_content = match.group(2)
        return frontmatter, doc_content

    def _search_by_topic(self, topic: str, doc_type: str | None = None) -> list[Path]:
        """Full-text search for topic."""
        topic_lower = topic.lower()
        results = []

        for path, data in self.docs.items():
            # Filter by type if specified
            if doc_type:
                fm_type = data["frontmatter"].get("type", "").lower()
                if fm_type != doc_type.lower():
                    continue

            # Search in content
            content = data["content"].lower()
            if topic_lower in content:
                # Calculate relevance score (occurrences)
                score = content.count(topic_lower)
                results.append((path, score))

        # Sort by relevance
        results.sort(key=lambda x: x[1], reverse=True)
        return [path for path, _ in results]

    def _filter_by_tags(self, tags: list[str]) -> list[Path]:
        """Filter docs by tags (AND logic - doc must have all tags)."""
        tags_lower = [t.lower() for t in tags]
        results = []

        for path, data in self.docs.items():
            fm = data["frontmatter"]
            doc_tags = fm.get("tags", [])
            if not isinstance(doc_tags, list):
                continue

            # Check if doc has all required tags
            doc_tags_lower = [t.lower() for t in doc_tags]
            if all(tag in doc_tags_lower for tag in tags_lower):
                results.append(path)

        return results

    def _filter_by_type(self, doc_type: str) -> list[Path]:
        """Filter docs by type (tutorial, how-to, reference, explanation)."""
        doc_type_lower = doc_type.lower()
        results = []

        for path, data in self.docs.items():
            fm = data["frontmatter"]
            fm_type = fm.get("type", "").lower()
            if fm_type == doc_type_lower:
                results.append(path)

        return results

    def _find_related(self, doc_path: str) -> list[Path]:
        """Find related docs via frontmatter 'related' field."""
        # Convert to Path
        target = Path(doc_path)
        if not target.is_absolute():
            target = self.root_dir / target

        if target not in self.docs:
            return []

        # Get related docs from frontmatter
        fm = self.docs[target]["frontmatter"]
        related = fm.get("related", [])
        if not isinstance(related, list):
            return []

        results = []
        for rel_path in related:
            # Try to resolve relative path
            for doc_path in self.docs.keys():
                if str(doc_path).endswith(rel_path):
                    results.append(doc_path)
                    break

        return results

    def _format_results(self, paths: list[Path], format_type: str) -> dict:
        """Format results for output."""
        results = []

        for path in paths:
            data = self.docs[path]
            fm = data["frontmatter"]

            # Relative path from root
            rel_path = path.relative_to(self.root_dir)

            result = {
                "path": str(rel_path),
                "title": fm.get("title", path.stem.replace("-", " ").title()),
                "type": fm.get("type", "unknown"),
            }

            if format_type == "json":
                # Include more details for JSON
                result["status"] = fm.get("status", "unknown")
                result["tags"] = fm.get("tags", [])
                result["last_updated"] = str(fm.get("last_updated", "unknown"))

                # Add preview (first 200 chars)
                content = data["content"]
                preview = content[:200].strip()
                if len(content) > 200:
                    preview += "..."
                result["preview"] = preview

            results.append(result)

        return {
            "count": len(results),
            "results": results,
        }

    def _output(self, data: dict) -> None:
        """Output results."""
        print(json.dumps(data, indent=2))


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Query documentation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--topic",
        help="Search for topic (full-text search)",
    )
    parser.add_argument(
        "--tag",
        action="append",
        help="Filter by tag (can specify multiple times for AND logic)",
    )
    parser.add_argument(
        "--type",
        choices=["tutorial", "how-to", "reference", "explanation"],
        help="Filter by documentation type",
    )
    parser.add_argument(
        "--related",
        help="Find related docs to specified doc path",
    )
    parser.add_argument(
        "--format",
        choices=["simple", "json"],
        default="simple",
        help="Output format (default: simple)",
    )

    args = parser.parse_args()

    # Validate args
    if not any([args.topic, args.tag, args.type, args.related]):
        parser.error("Must specify at least one query parameter")

    script_dir = Path(__file__).parent
    root_dir = script_dir.parent

    query = DocumentationQuery(root_dir)
    query.run(args)


if __name__ == "__main__":
    main()
