"""Shell script formatting rule for Makefile recipes."""

import re
from typing import Any

from ...plugins.base import FormatResult, FormatterPlugin


class ShellFormattingRule(FormatterPlugin):
    """Handles proper indentation of shell scripts within recipe lines."""

    def __init__(self) -> None:
        super().__init__("shell_formatting", priority=50)

    def format(
        self, lines: list[str], config: dict, check_mode: bool = False, **context: Any
    ) -> FormatResult:
        """Format shell script indentation within recipes."""
        formatted_lines = []
        changed = False
        errors: list[str] = []
        warnings: list[str] = []

        i = 0
        while i < len(lines):
            line = lines[i]

            # Check if this is a recipe line
            if line.startswith("\t") and line.strip():
                # Look for shell control structures
                stripped = line.lstrip("\t ")

                # Check if this starts a shell control structure
                if self._is_shell_control_start(stripped):
                    # Process the shell block
                    shell_block, block_end = self._extract_shell_block(lines, i)
                    formatted_block = self._format_shell_block(shell_block)

                    if formatted_block != shell_block:
                        changed = True

                    formatted_lines.extend(formatted_block)
                    i = block_end
                else:
                    formatted_lines.append(line)
                    i += 1
            else:
                formatted_lines.append(line)
                i += 1

        return FormatResult(
            lines=formatted_lines,
            changed=changed,
            errors=errors,
            warnings=warnings,
            check_messages=[],
        )

    def _is_shell_control_start(self, line: str) -> bool:
        """Check if a line starts a shell control structure."""
        # Strip make command prefixes (@, -, +)
        stripped = line.lstrip("@-+ ")

        # More precise matching than just startswith, to avoid matching substrings
        control_patterns = [
            r"^if\s+\[",
            r"^for\s+",
            r"^while\s+",
            r"^case\s+",
            r"^until\s+",
            r"^{\s*$",
        ]
        return any(re.match(pattern, stripped) for pattern in control_patterns)

    def _extract_shell_block(
        self, lines: list[str], start_idx: int
    ) -> tuple[list[str], int]:
        """Extract a shell control block from lines."""
        block = []
        i = start_idx

        while i < len(lines):
            line = lines[i]
            block.append(line)

            # If line doesn't end with continuation, this might be the end
            if not line.rstrip().endswith("\\"):
                i += 1
                break

            # Check for control structure end markers
            stripped = line.lstrip("\t ")
            if any(
                stripped.strip().startswith(end) for end in ["fi", "done", "esac", "}"]
            ):
                i += 1
                break

            i += 1

        return block, i

    def _format_shell_block(self, block: list[str]) -> list[str]:
        """Format a shell control block with proper indentation."""
        if not block:
            return block

        formatted = []
        indent_level = 0

        # Shell control structure keywords
        start_keywords = ("if", "for", "while", "case", "until")
        continuation_keywords = ("elif", "else")
        end_keywords = ("fi", "done", "esac")

        # Determine the base indentation level from the first line
        # This preserves the original indentation level instead of forcing it to 1 tab
        base_tabs = 1  # Default fallback
        if block and block[0].startswith("\t"):
            # Count leading tabs in the first line
            base_tabs = 0
            for char in block[0]:
                if char == "\t":
                    base_tabs += 1
                else:
                    break
            if base_tabs == 0:
                base_tabs = 1  # Fallback if no tabs found

        for line in block:
            if not line.strip():
                formatted.append(line)
                continue

            # Preserve the original line ending (including any trailing spaces)
            line_content = line.rstrip("\n\r")
            stripped = line_content.lstrip("\t ")

            # Check for trailing spaces/content after the main command
            trailing = ""
            if line_content.endswith(" "):
                # Count trailing spaces
                trailing_spaces = len(line_content) - len(line_content.rstrip(" "))
                trailing = " " * trailing_spaces
                stripped = stripped.rstrip(" ")

            # Strip make command prefixes for keyword detection
            command_content = stripped.lstrip("@-+ ")

            # Adjust indent level for closing keywords
            if any(
                command_content.strip().startswith(kw)
                for kw in continuation_keywords + end_keywords
            ):
                indent_level = max(0, indent_level - 1)

            # Calculate proper indentation, preserving base indentation level
            if indent_level == 0:
                # Primary recipe level - use base tabs from original indentation
                new_line = "\t" * base_tabs + stripped + trailing
            else:
                # Nested shell level - add extra tabs instead of mixing tabs and spaces
                new_line = "\t" * (base_tabs + indent_level) + stripped + trailing

            formatted.append(new_line)

            # Adjust indent level for opening keywords
            if any(
                command_content.strip().startswith(kw)
                for kw in start_keywords + continuation_keywords
            ) and stripped.rstrip().endswith("\\"):
                indent_level += 1

        return formatted
