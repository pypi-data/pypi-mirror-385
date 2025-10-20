"""Whitespace cleanup rule for Makefiles."""

from typing import Any

from ...plugins.base import FormatResult, FormatterPlugin


class WhitespaceRule(FormatterPlugin):
    """Handles trailing whitespace removal and line normalization."""

    def __init__(self) -> None:
        super().__init__(
            "whitespace", priority=45
        )  # Run late to clean up after other rules

    def format(
        self, lines: list[str], config: dict, check_mode: bool = False, **context: Any
    ) -> FormatResult:
        """Remove trailing whitespace and normalize empty lines."""
        formatted_lines = []
        changed = False
        errors: list[str] = []
        warnings: list[str] = []

        remove_trailing_whitespace = config.get("remove_trailing_whitespace", True)
        normalize_empty_lines = config.get("normalize_empty_lines", True)

        prev_was_empty = False

        for line in lines:
            # Remove trailing whitespace if enabled
            if remove_trailing_whitespace:
                cleaned_line = line.rstrip()
                if cleaned_line != line:
                    changed = True
                    line = cleaned_line

            # Normalize consecutive empty lines if enabled
            if normalize_empty_lines:
                is_empty = not line.strip()
                if is_empty and prev_was_empty:
                    # Skip this empty line (already have one)
                    changed = True
                    continue
                prev_was_empty = is_empty

            formatted_lines.append(line)

        # Remove extra trailing empty lines
        while (
            len(formatted_lines) > 1
            and formatted_lines[-1] == ""
            and formatted_lines[-2] == ""
        ):
            formatted_lines.pop()
            changed = True

        return FormatResult(
            lines=formatted_lines,
            changed=changed,
            errors=errors,
            warnings=warnings,
            check_messages=[],
        )
