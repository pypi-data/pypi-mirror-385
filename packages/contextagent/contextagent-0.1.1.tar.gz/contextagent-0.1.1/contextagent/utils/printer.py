"""
Rich-powered status printer for streaming pipeline progress updates.
"""

import json
import re
from typing import Any, Dict, List, Optional, Set, Tuple
from collections import OrderedDict

from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.markdown import Markdown
from rich.spinner import Spinner
from rich.syntax import Syntax
from rich.text import Text


class Printer:
    """Rich-powered status printer for streaming pipeline progress updates.

    - Each item is displayed as a Panel (box) with a title.
    - In-progress items show a spinner above the panel.
    - Completed items show a checkmark in the panel title (unless hidden).
    - Supports nested layout: groups (iterations) contain section panels.
    - Per-section border colors with sensible defaults.
    - Backward compatible with previous `update_item` signature.
    """

    # Default border colors by section name
    DEFAULT_BORDER_COLORS = {
        "observations": "yellow",
        "observation": "yellow",
        "observe": "yellow",
        "evaluation": "magenta",
        "evaluate": "magenta",
        "routing": "blue",
        "route": "blue",
        "tools": "cyan",
        "tool": "cyan",
        "writer": "green",
        "write": "green",
    }

    def __init__(self, console: Console) -> None:
        self.console = console
        # You can tweak screen=True to prevent scrollback; kept False to preserve logs
        self.live = Live(
            console=console,
            refresh_per_second=12,
            vertical_overflow="ellipsis",     # keep dashboard within viewport
            screen=False,                  # keep using normal screen buffer
            transient=True,               # clear live view when stopping
        )

        # items: id -> (content, is_done, title, border_style, group_id)
        self.items: Dict[str, Tuple[str, bool, Optional[str], Optional[str], Optional[str]]] = {}
        # Track which items should hide the done checkmark
        self.hide_done_ids: Set[str] = set()

        # Rich content produced by agents per iteration (title -> panel)
        self.iteration_sections: Dict[int, OrderedDict[str, Panel]] = {}
        # Original content strings for creating previews (title -> content_string)
        self.iteration_content: Dict[int, OrderedDict[str, str]] = {}
        self.iteration_order: List[int] = []
        self.finalized_iterations: Set[int] = set()

        # Group management
        self.group_order: List[str] = []  # Order of groups
        self.groups: Dict[str, Dict[str, Any]] = {}  # group_id -> {title, is_done, border_style, order}
        self.item_order: List[str] = []  # Order of top-level items (no group_id)

        self.live.start()

    def end(self) -> None:
        """Stop the live rendering session."""
        self.live.stop()

    def hide_done_checkmark(self, item_id: str) -> None:
        """Hide the completion checkmark for the given item id."""
        self.hide_done_ids.add(item_id)

    def start_group(
        self,
        group_id: str,
        *,
        title: Optional[str] = None,
        border_style: Optional[str] = None
    ) -> None:
        """Start a new group (e.g., an iteration panel).

        Args:
            group_id: Unique identifier for the group
            title: Optional title for the group panel
            border_style: Optional border color (defaults to white)
        """
        if group_id not in self.groups:
            self.group_order.append(group_id)
        self.groups[group_id] = {
            "title": title or group_id,
            "is_done": False,
            "border_style": border_style or "white",
            "order": []  # Track order of items in this group
        }
        self._flush()

    def end_group(
        self,
        group_id: str,
        *,
        is_done: bool = True,
        title: Optional[str] = None
    ) -> None:
        """Mark a group as complete.

        Args:
            group_id: Unique identifier for the group
            is_done: Whether the group is complete (default: True)
            title: Optional updated title for the group
        """
        if group_id in self.groups:
            self.groups[group_id]["is_done"] = is_done
            if title:
                self.groups[group_id]["title"] = title
            # Update border style to bright_white when done
            if is_done and self.groups[group_id]["border_style"] == "white":
                self.groups[group_id]["border_style"] = "bright_white"

        iteration = self._extract_iteration_index(group_id)
        if iteration is not None and is_done:
            self._finalize_iteration(iteration)
        else:
            self._flush()

    def update_item(
        self,
        item_id: str,
        content: str,
        *,
        is_done: bool = False,
        hide_checkmark: bool = False,
        title: Optional[str] = None,
        border_style: Optional[str] = None,
        group_id: Optional[str] = None,
    ) -> None:
        """Insert or update a status line and refresh the live console.

        Args:
            item_id: Unique identifier for the item
            content: Content to display
            is_done: Whether the task is complete
            hide_checkmark: Hide completion checkmark
            title: Optional panel title
            border_style: Optional border color (auto-detected from title if not provided)
            group_id: Optional group to nest this item in
        """
        # Auto-detect border style from title if not provided
        if border_style is None and title:
            title_lower = title.lower().strip()
            # Check for exact match first
            if title_lower in self.DEFAULT_BORDER_COLORS:
                border_style = self.DEFAULT_BORDER_COLORS[title_lower]
            else:
                # Check if any key is a substring of the title
                for key, color in self.DEFAULT_BORDER_COLORS.items():
                    if key in title_lower:
                        border_style = color
                        break

        # Track item in appropriate order list
        if item_id not in self.items:
            if group_id and group_id in self.groups:
                if item_id not in self.groups[group_id]["order"]:
                    self.groups[group_id]["order"].append(item_id)
            elif item_id not in self.item_order:
                self.item_order.append(item_id)

        self.items[item_id] = (content, is_done, title, border_style, group_id)
        if hide_checkmark:
            self.hide_done_ids.add(item_id)
        self._flush()

    def mark_item_done(
        self,
        item_id: str,
        *,
        title: Optional[str] = None,
        border_style: Optional[str] = None
    ) -> None:
        """Mark an existing status line as completed (optionally update title/border).

        Args:
            item_id: Unique identifier for the item
            title: Optional updated title
            border_style: Optional updated border color
        """
        if item_id in self.items:
            content, _, old_title, old_border, group_id = self.items[item_id]
            self.items[item_id] = (
                content,
                True,
                title or old_title,
                border_style or old_border,
                group_id
            )
            self._flush()

    def log_panel(
        self,
        title: str,
        content: str,
        *,
        border_style: Optional[str] = None,
        iteration: Optional[int] = None,
        group_id: Optional[str] = None,
    ) -> None:
        """Render a standalone panel outside the live dashboard.

        Useful for persisting rich text output to the terminal while keeping the
        live printer focused on lightweight status updates.

        Args:
            title: Panel title
            content: Panel content
            border_style: Optional border color
            iteration: Optional iteration number to group panels
            group_id: Optional group ID (currently unused, for future enhancements)
        """
        # content = self._truncate_content(content)

        if border_style is None:
            title_lower = title.lower().strip()
            if title_lower in self.DEFAULT_BORDER_COLORS:
                border_style = self.DEFAULT_BORDER_COLORS[title_lower]
            else:
                for key, color in self.DEFAULT_BORDER_COLORS.items():
                    if key in title_lower:
                        border_style = color
                        break

        panel = Panel(
            self._detect_and_render_body(content),
            title=Text(title),
            border_style=border_style or "cyan",
            padding=(1, 2),
            expand=True,
        )

        if iteration is not None:
            sections = self.iteration_sections.setdefault(iteration, OrderedDict())
            content_dict = self.iteration_content.setdefault(iteration, OrderedDict())
            if iteration not in self.iteration_order:
                self.iteration_order.append(iteration)
            sections[title] = panel
            content_dict[title] = content  # Store original content for previews
            if iteration in self.finalized_iterations:
                self.finalized_iterations.discard(iteration)
            self._flush()
        else:
            self.live.console.print(panel)

    # ------------ internals ------------

    def _truncate_content(self, content: str) -> str:
        """Limit panel body length so it fits comfortably in a terminal window."""
        max_lines = 40
        max_cols = 120
        lines = content.splitlines()
        truncated: List[str] = []

        for idx, line in enumerate(lines):
            shortened = line
            if len(shortened) > max_cols:
                shortened = shortened[: max_cols - 1].rstrip() + "…"
            truncated.append(shortened)
            if idx + 1 >= max_lines:
                if idx + 1 < len(lines):
                    truncated.append("…")
                break

        result = "\n".join(truncated)

        # Ensure code fences remain balanced after truncation
        if result.count("```") % 2 == 1:
            result += "\n```"
        return result

    def _detect_and_render_body(self, content: str) -> Any:
        """Auto-detect content type and render with appropriate Rich object.

        Detection order:
        1. ANSI escape codes → Text.from_ansi
        2. Rich markup (e.g., [bold cyan]...[/]) → Text.from_markup
        3. JSON → Syntax highlighting
        4. Code patterns → Syntax highlighting
        5. Markdown (headers, bold, bullets, code fences) → Markdown
        6. Plain text → Text
        """
        # Check for ANSI escape codes
        ansi_pattern = r'\x1b\[[0-9;]*m'
        if re.search(ansi_pattern, content):
            return Text.from_ansi(content)

        # Check for Rich markup patterns
        rich_markup_pattern = r'\[/?[a-z_]+(?:\s+[a-z_]+)*\]'
        if re.search(rich_markup_pattern, content, re.IGNORECASE):
            return Text.from_markup(content, emoji=True)

        # Check for JSON (starts with { or [, ends with } or ])
        stripped = content.strip()
        if (stripped.startswith('{') and stripped.endswith('}')) or \
           (stripped.startswith('[') and stripped.endswith(']')):
            try:
                json.loads(stripped)  # Validate it's valid JSON
                return Syntax(content, "json", theme="monokai", line_numbers=False)
            except (json.JSONDecodeError, ValueError):
                pass

        # Check for common code patterns (imports, function definitions, etc.)
        code_patterns = [
            r'^\s*import\s+',
            r'^\s*from\s+.+\s+import\s+',
            r'^\s*def\s+\w+\s*\(',
            r'^\s*class\s+\w+',
            r'^\s*async\s+def\s+',
            r'^\s*@\w+',
            r'^\s*if\s+__name__\s*==',
        ]

        for pattern in code_patterns:
            if re.search(pattern, content, re.MULTILINE):
                # Detect language
                if re.search(r'^\s*(import|from|def|class|async)', content, re.MULTILINE):
                    return Syntax(content, "python", theme="monokai", line_numbers=False)
                break

        # Check for markdown patterns (more aggressive detection)
        markdown_patterns = [
            r'^\s*#{1,6}\s+',           # Headers
            r'\*\*[^*]+\*\*',            # Bold
            r'\*[^*]+\*',                # Italic
            r'^\s*[\*\-\+]\s+',          # Unordered lists
            r'^\s*\d+\.\s+',             # Ordered lists
            r'```',                      # Code fences
            r'\[.+\]\(.+\)',             # Links
            r'^\s*>\s+',                 # Blockquotes
        ]

        for pattern in markdown_patterns:
            if re.search(pattern, content, re.MULTILINE):
                return Markdown(content, code_theme="monokai", inline_code_theme="monokai")

        # Default to plain text
        return Text(content)

    def _extract_iteration_index(self, group_id: str) -> Optional[int]:
        match = re.fullmatch(r"iter-(\d+)", group_id)
        if match:
            return int(match.group(1))
        return None

    def _build_iteration_panel(self, iteration: int) -> Optional[Panel]:
        sections = self.iteration_sections.get(iteration)
        if not sections:
            return None
        section_group = Group(*sections.values())
        return Panel(
            section_group,
            title=Text(f"Iteration {iteration}"),
            border_style="bright_white",
            padding=1,
            expand=True,
        )

    def _build_activity_preview_panel(self, iteration: int) -> Optional[Panel]:
        """Build a truncated preview panel showing only the current agent output.

        Args:
            iteration: The iteration number to preview

        Returns:
            A Panel with truncated preview of the most recent agent output, or None if no content
        """
        content_dict = self.iteration_content.get(iteration)
        if not content_dict:
            return None

        # Get only the most recent section (last item in OrderedDict)
        last_title = None
        last_content = None
        for title, content in content_dict.items():
            last_title = title
            last_content = content

        if not last_title or not last_content:
            return None

        # Truncate to first N lines and max characters to prevent long scrolling
        max_preview_lines = 12
        max_preview_chars = 2000
        lines = last_content.splitlines()
        preview_text = "\n".join(lines[:max_preview_lines])
        if len(lines) > max_preview_lines:
            preview_text += "\n..."

        # Also truncate by character count
        if len(preview_text) > max_preview_chars:
            preview_text = preview_text[:max_preview_chars] + "\n..."

        # Render the content using the same detection logic as log_panel
        preview_renderable = self._detect_and_render_body(preview_text)

        return Panel(
            preview_renderable,
            title=Text(f"Current Activity: {last_title}", style="bold cyan"),
            border_style="bright_black",
            padding=1,
            expand=True,
        )

    def _finalize_iteration(self, iteration: int) -> None:
        if iteration in self.finalized_iterations:
            return
        panel = self._build_iteration_panel(iteration)
        if panel:
            self.console.print(panel)
        self.finalized_iterations.add(iteration)
        self.iteration_sections.pop(iteration, None)
        self.iteration_content.pop(iteration, None)  # Also clean up content storage
        if iteration in self.iteration_order:
            self.iteration_order.remove(iteration)
        self._flush()

    def _render_item(
        self,
        item_id: str,
        content: str,
        is_done: bool,
        title: Optional[str],
        *,
        indent: int = 0,
    ) -> Any:
        """Render a single status line without surrounding boxes."""
        prefix = "✓" if is_done and item_id not in self.hide_done_ids else ("•" if is_done else "…")
        indent_str = " " * (indent * 2)
        lines = str(content).splitlines() or [""]

        label = title or item_id
        primary = lines[0].strip()
        if label and primary:
            display_text = f"{label}: {primary}"
        elif label:
            display_text = label
        elif primary:
            display_text = primary
        else:
            display_text = title or item_id or ""

        if not is_done:
            spinner_text = Text(f"{indent_str}{display_text}")
            spinner = Spinner("dots", text=spinner_text)
            if len(lines) == 1:
                return spinner
            continuation = [Text(f"{indent_str}  {line}") for line in lines[1:]]
            return Group(spinner, *continuation)

        headline = f"{indent_str}{prefix} {display_text}".rstrip()
        if not display_text:
            headline = f"{indent_str}{prefix}"
        first_line = Text(headline)
        if len(lines) == 1:
            return first_line
        continuation = [Text(f"{indent_str}  {line}") for line in lines[1:]]
        return Group(first_line, *continuation)

    def _render_group(self, group_id: str) -> Any:
        """Render a group panel containing its child section panels.

        Args:
            group_id: The group to render

        Returns:
            A Panel containing Group of child panels
        """
        group = self.groups[group_id]
        group_items: List[Any] = []

        # Render items in the order they were added to this group
        for item_id in group["order"]:
            if item_id in self.items:
                content, is_done, title, _border_style, _ = self.items[item_id]
                group_items.append(
                    self._render_item(item_id, content, is_done, title, indent=1)
                )

        status_symbol = "✓" if group["is_done"] else "…"
        header = Text(f"{status_symbol} {group['title']}")
        return Group(header, *(group_items or [Text("  (no activity)")]))

    def _flush(self) -> None:
        """Re-render the live view with the latest status items."""
        renderables: List[Any] = []

        # Render top-level items (those without group_id)
        for item_id in self.item_order:
            if item_id in self.items:
                content, is_done, title, _border_style, group_id = self.items[item_id]
                if group_id is None:
                    renderables.append(
                        self._render_item(item_id, content, is_done, title)
                    )

        # Render groups in order
        for group_id in self.group_order:
            if group_id in self.groups:
                renderables.append(self._render_group(group_id))

        render_groups: List[Any] = []

        # Status panel containing live progress lines
        status_body = Group(*renderables) if renderables else Text("No status yet")
        status_panel = Panel(
            status_body,
            title=Text("Status", style="bold"),
            border_style="bright_black",
            padding=(0, 1),
            expand=True,
        )
        render_groups.append(status_panel)

        # Show only the latest active iteration inside the live view
        active_iterations = [
            iteration
            for iteration in self.iteration_order
            if iteration not in self.finalized_iterations
            and self.iteration_sections.get(iteration)
        ]
        if active_iterations:
            current_iteration = max(active_iterations)

            # Add truncated preview panel for current activity only
            # (Full iteration panels are shown when finalized via _finalize_iteration)
            preview_panel = self._build_activity_preview_panel(current_iteration)
            if preview_panel:
                render_groups.append(preview_panel)

        self.live.update(Group(*render_groups))
