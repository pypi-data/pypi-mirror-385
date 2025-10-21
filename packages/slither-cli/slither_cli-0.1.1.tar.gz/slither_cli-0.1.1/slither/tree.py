"""Core directory traversal and rendering logic."""

from pathlib import Path
from typing import Optional, Callable
import fnmatch


class SlitherNode:
    """Represents a node in the directory tree."""

    def __init__(self, path: Path, is_last: bool = False):
        self.path = path
        self.is_last = is_last
        self.children: list[SlitherNode] = []


class SlitherBuilder:
    """Builds and renders a directory tree structure."""

    # Box-drawing characters for directory structure
    PIPE = "│   "
    TEE = "├── "
    ELBOW = "└── "
    BLANK = "    "

    def __init__(
        self,
        max_depth: Optional[int] = None,
        show_hidden: bool = False,
        dirs_only: bool = False,
        pattern: Optional[str] = None,
        ignore_pattern: Optional[str] = None,
        show_size: bool = False,
        human_readable: bool = False,
        sort_reverse: bool = False,
    ):
        self.max_depth = max_depth
        self.show_hidden = show_hidden
        self.dirs_only = dirs_only
        self.pattern = pattern
        self.ignore_pattern = ignore_pattern
        self.show_size = show_size
        self.human_readable = human_readable
        self.sort_reverse = sort_reverse

        # Stats
        self.dir_count = 0
        self.file_count = 0

    def should_include(self, path: Path) -> bool:
        """Determine if a path should be included in the output."""
        # Skip hidden files unless explicitly requested
        if not self.show_hidden and path.name.startswith('.'):
            return False

        # Check ignore pattern
        if self.ignore_pattern and fnmatch.fnmatch(path.name, self.ignore_pattern):
            return False

        # For directories, always include (they might have matching children)
        if path.is_dir():
            return True

        # If dirs_only, skip files
        if self.dirs_only:
            return False

        # Check include pattern
        if self.pattern and not fnmatch.fnmatch(path.name, self.pattern):
            return False

        return True

    def get_entries(self, directory: Path) -> list[Path]:
        """Get sorted directory entries."""
        try:
            entries = list(directory.iterdir())
        except PermissionError:
            return []

        # Filter entries
        entries = [e for e in entries if self.should_include(e)]

        # Sort: directories first, then by name
        entries.sort(
            key=lambda p: (not p.is_dir(), p.name.lower()),
            reverse=self.sort_reverse
        )

        return entries

    def format_size(self, size: int) -> str:
        """Format file size in human-readable format."""
        if not self.human_readable:
            return str(size)

        for unit in ['B', 'K', 'M', 'G', 'T']:
            if size < 1024.0:
                if unit == 'B':
                    return f"{size:.0f}"
                return f"{size:.1f}{unit}"
            size /= 1024.0
        return f"{size:.1f}P"

    def get_file_info(self, path: Path) -> str:
        """Get file size information if requested."""
        if not self.show_size:
            return ""

        try:
            if path.is_file():
                size = path.stat().st_size
                return f"[{self.format_size(size):>8}]  "
            elif path.is_dir():
                return f"[{'':>8}]  "
        except (PermissionError, OSError):
            pass

        return ""

    def build_tree(self, directory: Path, prefix: str = "", depth: int = 0) -> list[str]:
        """Recursively build the directory structure."""
        lines = []

        # Check max depth
        if self.max_depth is not None and depth >= self.max_depth:
            return lines

        # Get directory entries
        entries = self.get_entries(directory)

        for i, entry in enumerate(entries):
            is_last = i == len(entries) - 1

            # Determine the connector
            connector = self.ELBOW if is_last else self.TEE

            # Get file info
            file_info = self.get_file_info(entry)

            # Add the current entry
            lines.append(f"{prefix}{connector}{file_info}{entry.name}")

            # Update stats
            if entry.is_dir():
                self.dir_count += 1
            else:
                self.file_count += 1

            # Recurse into directories
            if entry.is_dir():
                extension = self.BLANK if is_last else self.PIPE
                lines.extend(
                    self.build_tree(entry, prefix + extension, depth + 1)
                )

        return lines

    def render(self, directory: Path) -> str:
        """Render the complete directory structure."""
        # Reset stats
        self.dir_count = 0
        self.file_count = 0

        # Start with the root directory
        lines = [str(directory.resolve())]

        # Build the structure
        tree_lines = self.build_tree(directory)
        lines.extend(tree_lines)

        # Add summary
        summary_parts = []
        if self.dir_count > 0:
            summary_parts.append(f"{self.dir_count} {'directory' if self.dir_count == 1 else 'directories'}")
        if not self.dirs_only:
            summary_parts.append(f"{self.file_count} {'file' if self.file_count == 1 else 'files'}")

        if summary_parts:
            lines.append("")
            lines.append(", ".join(summary_parts))

        return "\n".join(lines)
