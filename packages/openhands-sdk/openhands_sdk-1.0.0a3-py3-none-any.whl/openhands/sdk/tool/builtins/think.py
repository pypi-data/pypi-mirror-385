from collections.abc import Sequence

from pydantic import Field
from rich.text import Text

from openhands.sdk.llm.message import ImageContent, TextContent
from openhands.sdk.tool.tool import (
    Action,
    Observation,
    ToolAnnotations,
    ToolDefinition,
    ToolExecutor,
)


class ThinkAction(Action):
    """Action for logging a thought without making any changes."""

    thought: str = Field(description="The thought to log.")

    @property
    def visualize(self) -> Text:
        """Return Rich Text representation with thinking styling."""
        content = Text()

        # Add thinking icon and header
        content.append("🤔 ", style="yellow")
        content.append("Thinking: ", style="bold yellow")

        # Add the thought content with proper formatting
        if self.thought:
            # Split into lines for better formatting
            lines = self.thought.split("\n")
            for i, line in enumerate(lines):
                if i > 0:
                    content.append("\n")
                content.append(line.strip(), style="italic white")

        return content


class ThinkObservation(Observation):
    """Observation returned after logging a thought."""

    content: str = Field(
        default="Your thought has been logged.", description="Confirmation message."
    )

    @property
    def to_llm_content(self) -> Sequence[TextContent | ImageContent]:
        return [TextContent(text=self.content)]

    @property
    def visualize(self) -> Text:
        """Return Rich Text representation - empty since action shows the thought."""
        # Don't duplicate the thought display - action already shows it
        return Text()


THINK_DESCRIPTION = """Use the tool to think about something. It will not obtain new information or make any changes to the repository, but just log the thought. Use it when complex reasoning or brainstorming is needed.

Common use cases:
1. When exploring a repository and discovering the source of a bug, call this tool to brainstorm several unique ways of fixing the bug, and assess which change(s) are likely to be simplest and most effective.
2. After receiving test results, use this tool to brainstorm ways to fix failing tests.
3. When planning a complex refactoring, use this tool to outline different approaches and their tradeoffs.
4. When designing a new feature, use this tool to think through architecture decisions and implementation details.
5. When debugging a complex issue, use this tool to organize your thoughts and hypotheses.

The tool simply logs your thought process for better transparency and does not execute any code or make changes."""  # noqa: E501


class ThinkExecutor(ToolExecutor):
    def __call__(self, _: ThinkAction) -> ThinkObservation:
        return ThinkObservation()


ThinkTool = ToolDefinition(
    name="think",
    description=THINK_DESCRIPTION,
    action_type=ThinkAction,
    observation_type=ThinkObservation,
    executor=ThinkExecutor(),
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
