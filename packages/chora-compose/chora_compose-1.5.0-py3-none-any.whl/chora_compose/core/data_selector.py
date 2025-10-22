"""Data selector for extracting specific portions of content."""

import json
import re
from typing import Any

from jsonpath_ng import parse as jsonpath_parse


class DataSelectorError(Exception):
    """Raised when data selection fails."""

    pass


class DataSelector:
    """Extract specific data from content using selector syntax.

    Supports multiple selector types:
    - whole_content: Return entire content (default/passthrough)
    - Line ranges: "10-20", ":50", "100:" (Python slice syntax)
    - JSONPath: "$.path.to.data" (JSONPath expressions)
    - Markdown sections: "# Heading Name" (extract by heading)
    - Code functions: "function:name" (extract function/class)
    """

    def select(self, data: Any, selector: str | None = None) -> Any:
        """Select data using the specified selector.

        Args:
            data: Source data (string, dict, list, etc.)
            selector: Selector expression, or None for whole content

        Returns:
            Selected data

        Raises:
            DataSelectorError: If selection fails
            ValueError: If selector format is invalid
        """
        # Default to whole content
        if not selector or selector == "whole_content":
            return data

        # Determine selector type and dispatch
        try:
            # JSONPath selector (starts with $.)
            if selector.startswith("$."):
                return self.select_jsonpath(data, selector)

            # Markdown heading selector (starts with #)
            elif selector.startswith("#"):
                return self.select_markdown_section(data, selector)

            # Function/class selector (starts with function: or class:)
            elif selector.startswith(("function:", "class:")):
                return self.select_code_element(data, selector)

            # Line range selector (matches patterns like 10-20, :50, 100:)
            elif re.match(r"^(\d+)?[-:](\d+)?$", selector):
                return self.select_line_range(data, selector)

            else:
                raise ValueError(
                    f"Unknown selector format: '{selector}'. "
                    f"Expected: whole_content, $.jsonpath, #heading, "
                    f"function:name, or line range (10-20, :50, 100:)"
                )

        except DataSelectorError:
            raise
        except Exception as e:
            raise DataSelectorError(
                f"Failed to apply selector '{selector}': {e}"
            ) from e

    def select_jsonpath(self, data: Any, path: str) -> Any:
        """Extract data using JSONPath expression.

        Args:
            data: Source data (dict, list, or JSON string)
            path: JSONPath expression (e.g., "$.users[0].name")

        Returns:
            Matched data (single value or list of matches)

        Raises:
            DataSelectorError: If JSONPath fails or no matches found
        """
        # Parse JSON if data is a string
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError as e:
                raise DataSelectorError(
                    f"Cannot apply JSONPath to non-JSON string: {e}"
                ) from e

        # Parse and apply JSONPath
        try:
            expr = jsonpath_parse(path)
            matches = [match.value for match in expr.find(data)]
        except Exception as e:
            raise DataSelectorError(f"Invalid JSONPath expression '{path}': {e}") from e

        # Return results
        if not matches:
            raise DataSelectorError(f"JSONPath '{path}' matched no data")

        # Return single value if only one match, otherwise return list
        return matches[0] if len(matches) == 1 else matches

    def select_line_range(self, data: str, range_spec: str) -> str:
        """Extract line range from text.

        Supports Python slice syntax:
        - "10-20" or "10:20": Lines 10 through 20
        - ":50": First 50 lines
        - "100:": From line 100 to end
        - "5-5" or "5:5": Just line 5

        Args:
            data: Source text
            range_spec: Range specification

        Returns:
            Selected lines as string

        Raises:
            DataSelectorError: If range is invalid
        """
        if not isinstance(data, str):
            raise DataSelectorError(
                f"Line range selector requires string data, got {type(data).__name__}"
            )

        lines = data.splitlines(keepends=True)
        total_lines = len(lines)

        # Parse range specification (support both - and : as separators)
        separator = "-" if "-" in range_spec else ":"
        parts = range_spec.split(separator)

        try:
            # Parse start and end indices
            start = int(parts[0]) - 1 if parts[0] else 0  # 1-indexed to 0-indexed
            end = int(parts[1]) if parts[1] else total_lines

            # Validate range
            if start < 0:
                start = 0
            if end > total_lines:
                end = total_lines
            if start >= end and end != 0:
                raise DataSelectorError(
                    f"Invalid range: start ({start + 1}) >= end ({end})"
                )

            # Extract lines
            selected_lines = lines[start:end]

            if not selected_lines:
                raise DataSelectorError(
                    f"Line range {range_spec} is empty or out of bounds "
                    f"(total lines: {total_lines})"
                )

            return "".join(selected_lines)

        except ValueError as e:
            raise DataSelectorError(
                f"Invalid line range format '{range_spec}': {e}"
            ) from e

    def select_markdown_section(self, data: str, heading: str) -> str:
        """Extract markdown section by heading.

        Args:
            data: Source markdown text
            heading: Heading text (e.g., "# Introduction" or "## Setup")

        Returns:
            Section content including heading

        Raises:
            DataSelectorError: If heading not found
        """
        if not isinstance(data, str):
            raise DataSelectorError(
                f"Markdown selector requires string data, got {type(data).__name__}"
            )

        # Normalize heading (remove extra # symbols if needed)
        heading_text = heading.lstrip("#").strip()

        # Find the heading level (count # symbols)
        heading_level = len(heading) - len(heading.lstrip("#"))
        if heading_level == 0:
            heading_level = 1  # Default to h1 if no # provided

        lines = data.splitlines(keepends=True)
        section_lines = []
        found_heading = False
        in_section = False

        for line in lines:
            # Check if this line is a heading
            heading_match = re.match(r"^(#{1,6})\s+(.+)", line)

            if heading_match:
                level = len(heading_match.group(1))
                text = heading_match.group(2).strip()

                # Found our target heading
                if text.lower() == heading_text.lower() and (
                    heading_level == 0 or level == heading_level
                ):
                    found_heading = True
                    in_section = True
                    section_lines.append(line)

                # Found a same-level or higher-level heading (end of section)
                elif in_section and level <= heading_level:
                    break

                # In section but different heading
                elif in_section:
                    section_lines.append(line)

            # Regular content line
            elif in_section:
                section_lines.append(line)

        if not found_heading:
            raise DataSelectorError(
                f"Markdown heading '{heading}' not found in content"
            )

        return "".join(section_lines)

    def select_code_element(self, data: str, element_spec: str) -> str:
        """Extract function or class from code.

        Uses simple regex matching for common patterns.
        Supports Python and JavaScript-like syntax.

        Args:
            data: Source code
            element_spec: Element specification (e.g., "function:getUserData"
                         or "class:UserModel")

        Returns:
            Code element definition

        Raises:
            DataSelectorError: If element not found
        """
        if not isinstance(data, str):
            raise DataSelectorError(
                f"Code selector requires string data, got {type(data).__name__}"
            )

        # Parse element specification
        parts = element_spec.split(":", 1)
        if len(parts) != 2:
            raise ValueError(
                f"Invalid element specification '{element_spec}'. "
                f"Expected 'function:name' or 'class:name'"
            )

        element_type, element_name = parts
        lines = data.splitlines(keepends=True)

        # Define patterns for different element types
        if element_type == "function":
            # Python: def name(...) or async def name(...)
            # JavaScript: function name(...) or async function name(...)
            patterns = [
                rf"^(\s*)(?:async\s+)?def\s+{re.escape(element_name)}\s*\(",
                rf"^(\s*)(?:async\s+)?function\s+{re.escape(element_name)}\s*\(",
                rf"^(\s*)const\s+{re.escape(element_name)}\s*=\s*(?:async\s+)?\(",
                rf"^(\s*){re.escape(element_name)}\s*:\s*function\s*\(",
            ]
        elif element_type == "class":
            # Python: class Name(...):
            # JavaScript: class Name ...
            patterns = [
                rf"^(\s*)class\s+{re.escape(element_name)}\s*[\(:]",
            ]
        else:
            raise ValueError(
                f"Unsupported element type '{element_type}'. "
                f"Expected 'function' or 'class'"
            )

        # Search for element
        element_lines = []
        found_element = False
        base_indent = 0

        for i, line in enumerate(lines):
            # Try to match any pattern
            if not found_element:
                for pattern in patterns:
                    match = re.match(pattern, line)
                    if match:
                        found_element = True
                        base_indent = len(match.group(1))
                        element_lines.append(line)
                        break

            # Collect indented lines that belong to the element
            elif found_element:
                # Empty line or comment
                if not line.strip() or line.strip().startswith("#"):
                    element_lines.append(line)

                # Indented line (part of element)
                elif len(line) - len(line.lstrip()) > base_indent:
                    element_lines.append(line)

                # Same or less indentation (end of element)
                else:
                    break

        if not found_element:
            raise DataSelectorError(
                f"Code element '{element_type}:{element_name}' not found in source"
            )

        return "".join(element_lines)
