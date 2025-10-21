"""Grep tool implementation for fast content search."""

import os
from collections.abc import Sequence
from typing import TYPE_CHECKING

from pydantic import Field


if TYPE_CHECKING:
    from openhands.sdk.conversation.state import ConversationState

from openhands.sdk.llm import ImageContent, TextContent
from openhands.sdk.tool import Action, Observation, ToolAnnotations, ToolDefinition


class GrepAction(Action):
    """Schema for grep content search operations."""

    pattern: str = Field(description="The regex pattern to search for in file contents")
    path: str | None = Field(
        default=None,
        description=(
            "The directory (absolute path) to search in. "
            "Defaults to the current working directory."
        ),
    )
    include: str | None = Field(
        default=None,
        description=(
            "Optional file pattern to filter which files to search "
            '(e.g., "*.js", "*.{ts,tsx}")'
        ),
    )


class GrepObservation(Observation):
    """Observation from grep content search operations."""

    matches: list[str] = Field(description="List of file paths containing the pattern")
    pattern: str = Field(description="The regex pattern that was used")
    search_path: str = Field(description="The directory that was searched")
    include_pattern: str | None = Field(
        default=None, description="The file pattern filter that was used"
    )
    truncated: bool = Field(
        default=False, description="Whether results were truncated to 100 files"
    )
    error: str | None = Field(default=None, description="Error message if any")

    @property
    def to_llm_content(self) -> Sequence[TextContent | ImageContent]:
        """Convert observation to LLM content."""
        if self.error:
            return [TextContent(text=f"Error: {self.error}")]

        if not self.matches:
            include_info = (
                f" (filtered by '{self.include_pattern}')"
                if self.include_pattern
                else ""
            )
            content = (
                f"No files found containing pattern '{self.pattern}' "
                f"in directory '{self.search_path}'{include_info}"
            )
        else:
            include_info = (
                f" (filtered by '{self.include_pattern}')"
                if self.include_pattern
                else ""
            )
            file_list = "\n".join(self.matches)
            content = (
                f"Found {len(self.matches)} file(s) containing pattern "
                f"'{self.pattern}' in '{self.search_path}'{include_info}:\n"
                f"{file_list}"
            )
            if self.truncated:
                content += (
                    "\n\n[Results truncated to first 100 files. "
                    "Consider using a more specific pattern.]"
                )

        return [TextContent(text=content)]


TOOL_DESCRIPTION = """Fast content search tool.
* Searches file contents using regular expressions
* Supports full regex syntax (eg. "log.*Error", "function\\s+\\w+", etc.)
* Filter files by pattern with the include parameter (eg. "*.js", "*.{ts,tsx}")
* Returns matching file paths sorted by modification time.
* Only the first 100 results are returned. Consider narrowing your search with stricter regex patterns or provide path parameter if you need more results.
* Use this tool when you need to find files containing specific patterns.
"""  # noqa


class GrepTool(ToolDefinition[GrepAction, GrepObservation]):
    """A ToolDefinition subclass that automatically initializes a GrepExecutor."""

    @classmethod
    def create(
        cls,
        conv_state: "ConversationState",
    ) -> Sequence["GrepTool"]:
        """Initialize GrepTool with a GrepExecutor.

        Args:
            conv_state: Conversation state to get working directory from.
                         If provided, working_dir will be taken from
                         conv_state.workspace
        """
        # Import here to avoid circular imports
        from openhands.tools.grep.impl import GrepExecutor

        working_dir = conv_state.workspace.working_dir
        if not os.path.isdir(working_dir):
            raise ValueError(f"working_dir '{working_dir}' is not a valid directory")

        # Initialize the executor
        executor = GrepExecutor(working_dir=working_dir)

        # Add working directory information to the tool description
        enhanced_description = (
            f"{TOOL_DESCRIPTION}\n\n"
            f"Your current working directory is: {working_dir}\n"
            f"When searching for content, searches are performed in this directory."
        )

        # Initialize the parent ToolDefinition with the executor
        return [
            cls(
                name="grep",
                description=enhanced_description,
                action_type=GrepAction,
                observation_type=GrepObservation,
                annotations=ToolAnnotations(
                    title="grep",
                    readOnlyHint=True,
                    destructiveHint=False,
                    idempotentHint=True,
                    openWorldHint=False,
                ),
                executor=executor,
            )
        ]
