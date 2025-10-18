"""Glob tool implementation for fast file pattern matching."""

import os
from collections.abc import Sequence
from typing import TYPE_CHECKING

from pydantic import Field


if TYPE_CHECKING:
    from openhands.sdk.conversation.state import ConversationState

from openhands.sdk.llm import ImageContent, TextContent
from openhands.sdk.tool import Action, Observation, ToolAnnotations, ToolDefinition


class GlobAction(Action):
    """Schema for glob pattern matching operations."""

    pattern: str = Field(
        description='The glob pattern to match files (e.g., "**/*.js", "src/**/*.ts")'
    )
    path: str | None = Field(
        default=None,
        description=(
            "The directory (absolute path) to search in. "
            "Defaults to the current working directory."
        ),
    )


class GlobObservation(Observation):
    """Observation from glob pattern matching operations."""

    files: list[str] = Field(
        description="List of matching file paths sorted by modification time"
    )
    pattern: str = Field(description="The glob pattern that was used")
    search_path: str = Field(description="The directory that was searched")
    truncated: bool = Field(
        default=False, description="Whether results were truncated to 100 files"
    )
    error: str | None = Field(default=None, description="Error message if any")

    @property
    def to_llm_content(self) -> Sequence[TextContent | ImageContent]:
        """Convert observation to LLM content."""
        if self.error:
            return [TextContent(text=f"Error: {self.error}")]

        if not self.files:
            content = (
                f"No files found matching pattern '{self.pattern}' "
                f"in directory '{self.search_path}'"
            )
        else:
            file_list = "\n".join(self.files)
            content = (
                f"Found {len(self.files)} file(s) matching pattern "
                f"'{self.pattern}' in '{self.search_path}':\n{file_list}"
            )
            if self.truncated:
                content += (
                    "\n\n[Results truncated to first 100 files. "
                    "Consider using a more specific pattern.]"
                )

        return [TextContent(text=content)]


TOOL_DESCRIPTION = """Fast file pattern matching tool.
* Supports glob patterns like "**/*.js" or "src/**/*.ts"
* Use this tool when you need to find files by name patterns
* Returns matching file paths sorted by modification time
* Only the first 100 results are returned. Consider narrowing your search with stricter glob patterns or provide path parameter if you need more results.

Examples:
- Find all JavaScript files: "**/*.js"
- Find TypeScript files in src: "src/**/*.ts"
- Find Python test files: "**/test_*.py"
- Find configuration files: "**/*.{json,yaml,yml,toml}"
"""  # noqa


class GlobTool(ToolDefinition[GlobAction, GlobObservation]):
    """A ToolDefinition subclass that automatically initializes a GlobExecutor."""

    @classmethod
    def create(
        cls,
        conv_state: "ConversationState",
    ) -> Sequence["GlobTool"]:
        """Initialize GlobTool with a GlobExecutor.

        Args:
            conv_state: Conversation state to get working directory from.
                         If provided, working_dir will be taken from
                         conv_state.workspace
        """
        # Import here to avoid circular imports
        from openhands.tools.glob.impl import GlobExecutor

        working_dir = conv_state.workspace.working_dir
        if not os.path.isdir(working_dir):
            raise ValueError(f"working_dir '{working_dir}' is not a valid directory")

        # Initialize the executor
        executor = GlobExecutor(working_dir=working_dir)

        # Add working directory information to the tool description
        enhanced_description = (
            f"{TOOL_DESCRIPTION}\n\n"
            f"Your current working directory is: {working_dir}\n"
            f"When searching for files, patterns are relative to this directory."
        )

        # Initialize the parent ToolDefinition with the executor
        return [
            cls(
                name="glob",
                description=enhanced_description,
                action_type=GlobAction,
                observation_type=GlobObservation,
                annotations=ToolAnnotations(
                    title="glob",
                    readOnlyHint=True,
                    destructiveHint=False,
                    idempotentHint=True,
                    openWorldHint=False,
                ),
                executor=executor,
            )
        ]
