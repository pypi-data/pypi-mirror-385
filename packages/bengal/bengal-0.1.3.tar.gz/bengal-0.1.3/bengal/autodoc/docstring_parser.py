"""
Docstring parsers for different styles.

Supports:
- Google style (Args:, Returns:, Raises:, Example:)
- NumPy style (Parameters, Returns, Raises, Examples with --------)
- Sphinx style (:param name:, :returns:, :raises:)
"""


from __future__ import annotations

import re
from typing import Any


class ParsedDocstring:
    """Container for parsed docstring data."""

    def __init__(self):
        self.summary: str = ""
        self.description: str = ""
        self.args: dict[str, str] = {}
        self.returns: str = ""
        self.return_type: str | None = None
        self.raises: list[dict[str, str]] = []
        self.examples: list[str] = []
        self.see_also: list[str] = []
        self.notes: list[str] = []
        self.warnings: list[str] = []
        self.deprecated: str | None = None
        self.version_added: str | None = None
        self.attributes: dict[str, str] = {}

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "summary": self.summary,
            "description": self.description,
            "args": self.args,
            "returns": self.returns,
            "return_type": self.return_type,
            "raises": self.raises,
            "examples": self.examples,
            "see_also": self.see_also,
            "notes": self.notes,
            "warnings": self.warnings,
            "deprecated": self.deprecated,
            "version_added": self.version_added,
            "attributes": self.attributes,
        }


def parse_docstring(docstring: str | None, style: str = "auto") -> ParsedDocstring:
    """
    Parse docstring and extract structured information.

    Args:
        docstring: Raw docstring text
        style: Docstring style ('auto', 'google', 'numpy', 'sphinx')

    Returns:
        ParsedDocstring object with extracted information
    """
    if not docstring:
        return ParsedDocstring()

    # Auto-detect style
    if style == "auto":
        style = detect_docstring_style(docstring)

    # Parse based on detected style
    if style == "google":
        return GoogleDocstringParser().parse(docstring)
    elif style == "numpy":
        return NumpyDocstringParser().parse(docstring)
    elif style == "sphinx":
        return SphinxDocstringParser().parse(docstring)
    else:
        # Plain docstring - just summary
        result = ParsedDocstring()
        result.summary = docstring.strip().split("\n")[0]
        result.description = docstring.strip()
        return result


def detect_docstring_style(docstring: str) -> str:
    """
    Auto-detect docstring style.

    Args:
        docstring: Raw docstring text

    Returns:
        Style name ('google', 'numpy', 'sphinx', or 'plain')
    """
    # Google style markers
    if re.search(
        r"\n\s*(Args|Arguments|Parameters|Returns?|Yields?|Raises?|Note|Warning|Example|Examples|See Also|Attributes):\s*\n",
        docstring,
    ):
        return "google"

    # NumPy style markers (section with underline)
    if re.search(
        r"\n\s*(Parameters|Returns?|Yields?|Raises?|See Also|Notes?|Warnings?|Examples?|Attributes)\s*\n\s*-+\s*\n",
        docstring,
    ):
        return "numpy"

    # Sphinx style markers
    if re.search(r":param |:type |:returns?:|:rtype:|:raises?:", docstring):
        return "sphinx"

    return "plain"


class GoogleDocstringParser:
    """
    Parse Google-style docstrings.

    Example:
        Args:
            name (str): The name to greet
            loud (bool): Whether to shout

        Returns:
            str: The greeting message

        Raises:
            ValueError: If name is empty

        Example:
            >>> greet("World", loud=True)
            'HELLO, WORLD!'
    """

    def parse(self, docstring: str) -> ParsedDocstring:
        """Parse Google-style docstring."""
        result = ParsedDocstring()

        # Split into lines
        lines = docstring.split("\n")

        # Extract summary (first line)
        if lines:
            result.summary = lines[0].strip()

        # Split into sections
        sections = self._split_sections(docstring)

        # Parse each section
        result.description = sections.get("description", result.summary)
        result.args = self._parse_args_section(sections.get("Args", ""))
        if not result.args:
            result.args = self._parse_args_section(sections.get("Arguments", ""))
        if not result.args:
            result.args = self._parse_args_section(sections.get("Parameters", ""))

        result.returns = sections.get("Returns", sections.get("Return", ""))
        result.raises = self._parse_raises_section(sections.get("Raises", ""))
        result.examples = self._parse_examples_section(
            sections.get("Example", sections.get("Examples", ""))
        )
        result.see_also = self._parse_see_also_section(sections.get("See Also", ""))
        result.notes = self._parse_note_section(sections.get("Note", sections.get("Notes", "")))
        result.warnings = self._parse_note_section(
            sections.get("Warning", sections.get("Warnings", ""))
        )
        result.deprecated = sections.get("Deprecated")
        result.attributes = self._parse_args_section(sections.get("Attributes", ""))

        return result

    def _split_sections(self, docstring: str) -> dict[str, str]:
        """Split docstring into sections."""
        sections = {}
        lines = docstring.split("\n")

        # Section markers
        section_markers = [
            "Args",
            "Arguments",
            "Parameters",
            "Returns",
            "Return",
            "Yields",
            "Yield",
            "Raises",
            "Raise",
            "Note",
            "Notes",
            "Warning",
            "Warnings",
            "Example",
            "Examples",
            "See Also",
            "Deprecated",
            "Attributes",
        ]

        current_section = "description"
        section_buffer = []

        for line in lines:
            stripped = line.strip()

            # Check if this line is a section header
            is_section = False
            for marker in section_markers:
                if stripped == f"{marker}:":
                    # Save previous section
                    if section_buffer:
                        sections[current_section] = "\n".join(section_buffer).strip()
                        section_buffer = []
                    current_section = marker
                    is_section = True
                    break

            if not is_section:
                section_buffer.append(line)

        # Save last section
        if section_buffer:
            sections[current_section] = "\n".join(section_buffer).strip()

        return sections

    def _parse_args_section(self, section: str) -> dict[str, str]:
        """
        Parse Args section.

        Format:
            name (type): description
            name: description
        """
        args = {}
        if not section:
            return args

        lines = section.split("\n")
        current_arg = None
        current_desc = []

        for line in lines:
            # Check if this is a new argument
            # Pattern: "name (type): description" or "name: description"
            match = re.match(r"^\s*(\w+)\s*(?:\(([^)]+)\))?\s*:\s*(.+)?", line)
            if match:
                # Save previous arg
                if current_arg:
                    args[current_arg] = " ".join(current_desc).strip()

                # Start new arg
                current_arg = match.group(1)
                desc = match.group(3) or ""
                current_desc = [desc] if desc else []
            elif current_arg and line.strip():
                # Continuation of description
                current_desc.append(line.strip())

        # Save last arg
        if current_arg:
            args[current_arg] = " ".join(current_desc).strip()

        return args

    def _parse_raises_section(self, section: str) -> list[dict[str, str]]:
        """
        Parse Raises section.

        Format:
            ExceptionType: description
        """
        raises = []
        if not section:
            return raises

        lines = section.split("\n")
        current_exc = None
        current_desc = []

        for line in lines:
            match = re.match(r"^\s*(\w+)\s*:\s*(.+)?", line)
            if match:
                # Save previous exception
                if current_exc:
                    raises.append(
                        {"type": current_exc, "description": " ".join(current_desc).strip()}
                    )

                # Start new exception
                current_exc = match.group(1)
                desc = match.group(2) or ""
                current_desc = [desc] if desc else []
            elif current_exc and line.strip():
                current_desc.append(line.strip())

        # Save last exception
        if current_exc:
            raises.append({"type": current_exc, "description": " ".join(current_desc).strip()})

        return raises

    def _parse_examples_section(self, section: str) -> list[str]:
        """Extract code examples."""
        examples = []
        if not section:
            return examples

        # Look for >>> or code blocks
        in_example = False
        current_example = []

        for line in section.split("\n"):
            if ">>>" in line or line.strip().startswith("```"):
                in_example = True
                current_example.append(line)
            elif in_example:
                current_example.append(line)
                if line.strip().endswith("```") and len(current_example) > 1:
                    examples.append("\n".join(current_example))
                    current_example = []
                    in_example = False
            elif line.strip() and not in_example:
                # Non-code text, might be example description
                if not current_example:
                    current_example.append(line)

        if current_example:
            examples.append("\n".join(current_example))

        return examples

    def _parse_see_also_section(self, section: str) -> list[str]:
        """Extract cross-references."""
        see_also = []
        if not section:
            return see_also

        for line in section.split("\n"):
            line = line.strip()
            if line:
                # Extract references (simple: just capture non-empty lines)
                see_also.append(line)

        return see_also

    def _parse_note_section(self, section: str) -> list[str]:
        """Extract notes or warnings."""
        notes = []
        if not section:
            return notes

        # Split by paragraphs
        current_note = []
        for line in section.split("\n"):
            if line.strip():
                current_note.append(line.strip())
            elif current_note:
                notes.append(" ".join(current_note))
                current_note = []

        if current_note:
            notes.append(" ".join(current_note))

        return notes


class NumpyDocstringParser:
    """
    Parse NumPy-style docstrings.

    Example:
        Parameters
        ----------
        name : str
            The name to greet
        loud : bool, optional
            Whether to shout (default: False)

        Returns
        -------
        str
            The greeting message
    """

    def parse(self, docstring: str) -> ParsedDocstring:
        """Parse NumPy-style docstring."""
        result = ParsedDocstring()

        # Extract summary
        lines = docstring.split("\n")
        if lines:
            result.summary = lines[0].strip()

        # Split into sections
        sections = self._split_sections(docstring)

        # Parse sections
        result.description = sections.get("description", result.summary)
        result.args = self._parse_parameters_section(sections.get("Parameters", ""))
        result.returns = sections.get("Returns", "")
        result.raises = self._parse_raises_section(sections.get("Raises", ""))
        result.examples = self._parse_examples_section(sections.get("Examples", ""))
        result.see_also = self._parse_see_also_section(sections.get("See Also", ""))
        result.notes = self._parse_note_section(sections.get("Notes", ""))
        result.warnings = self._parse_note_section(sections.get("Warnings", ""))
        result.attributes = self._parse_parameters_section(sections.get("Attributes", ""))

        return result

    def _split_sections(self, docstring: str) -> dict[str, str]:
        """Split NumPy docstring into sections."""
        sections = {}
        lines = docstring.split("\n")

        section_markers = [
            "Parameters",
            "Returns",
            "Yields",
            "Raises",
            "See Also",
            "Notes",
            "Warnings",
            "Examples",
            "Attributes",
            "Methods",
        ]

        current_section = "description"
        section_buffer = []
        i = 0

        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            # Check if this is a section header (followed by -----)
            if stripped in section_markers and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line and all(c == "-" for c in next_line):
                    # Save previous section
                    if section_buffer:
                        sections[current_section] = "\n".join(section_buffer).strip()
                        section_buffer = []

                    current_section = stripped
                    i += 2  # Skip header and underline
                    continue

            section_buffer.append(line)
            i += 1

        # Save last section
        if section_buffer:
            sections[current_section] = "\n".join(section_buffer).strip()

        return sections

    def _parse_parameters_section(self, section: str) -> dict[str, str]:
        """
        Parse Parameters section.

        Format:
            name : type
                description
        """
        params = {}
        if not section:
            return params

        lines = section.split("\n")
        current_param = None
        current_desc = []

        for line in lines:
            # Check for parameter definition: "name : type"
            if ":" in line and not line.startswith(" "):
                # Save previous param
                if current_param:
                    params[current_param] = " ".join(current_desc).strip()

                # Parse new param
                parts = line.split(":", 1)
                current_param = parts[0].strip()
                current_desc = []
            elif current_param and line.strip():
                # Description line (indented)
                current_desc.append(line.strip())

        # Save last param
        if current_param:
            params[current_param] = " ".join(current_desc).strip()

        return params

    def _parse_raises_section(self, section: str) -> list[dict[str, str]]:
        """Parse Raises section (similar to Parameters)."""
        raises = []
        if not section:
            return raises

        lines = section.split("\n")
        current_exc = None
        current_desc = []

        for line in lines:
            if not line.startswith(" ") and line.strip():
                # Save previous exception
                if current_exc:
                    raises.append(
                        {"type": current_exc, "description": " ".join(current_desc).strip()}
                    )

                # New exception type
                current_exc = line.strip()
                current_desc = []
            elif current_exc and line.strip():
                current_desc.append(line.strip())

        # Save last exception
        if current_exc:
            raises.append({"type": current_exc, "description": " ".join(current_desc).strip()})

        return raises

    def _parse_examples_section(self, section: str) -> list[str]:
        """Extract examples (usually code blocks)."""
        if not section:
            return []
        return [section.strip()]

    def _parse_see_also_section(self, section: str) -> list[str]:
        """Extract cross-references."""
        if not section:
            return []
        return [line.strip() for line in section.split("\n") if line.strip()]

    def _parse_note_section(self, section: str) -> list[str]:
        """Extract notes."""
        if not section:
            return []
        return [section.strip()]


class SphinxDocstringParser:
    """
    Parse Sphinx-style docstrings.

    Example:
        :param name: The name to greet
        :type name: str
        :param loud: Whether to shout
        :type loud: bool
        :returns: The greeting message
        :rtype: str
        :raises ValueError: If name is empty
    """

    def parse(self, docstring: str) -> ParsedDocstring:
        """Parse Sphinx-style docstring."""
        result = ParsedDocstring()

        lines = docstring.split("\n")

        # Extract summary (first non-field line)
        summary_lines = []
        for line in lines:
            if not line.strip().startswith(":"):
                summary_lines.append(line)
            else:
                break

        if summary_lines:
            result.summary = summary_lines[0].strip()
            result.description = "\n".join(summary_lines).strip()

        # Parse field lists
        for line in lines:
            line = line.strip()

            # :param name: description
            match = re.match(r":param\s+(\w+):\s*(.+)", line)
            if match:
                param_name = match.group(1)
                param_desc = match.group(2)
                result.args[param_name] = param_desc
                continue

            # :returns: or :return: description
            match = re.match(r":returns?:\s*(.+)", line)
            if match:
                result.returns = match.group(1)
                continue

            # :rtype: type
            match = re.match(r":rtype:\s*(.+)", line)
            if match:
                result.return_type = match.group(1)
                continue

            # :raises Exception: description
            match = re.match(r":raises?\s+(\w+):\s*(.+)?", line)
            if match:
                exc_type = match.group(1)
                exc_desc = match.group(2) or ""
                result.raises.append({"type": exc_type, "description": exc_desc})
                continue

        return result
