from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from pydantic import Field

from openhands.sdk.logger import get_logger
from openhands.sdk.utils.models import DiscriminatedUnionMixin
from openhands.sdk.workspace.models import CommandResult, FileOperationResult


logger = get_logger(__name__)


class BaseWorkspace(DiscriminatedUnionMixin, ABC):
    """Abstract base mixin for workspace.

    All workspace implementations support the context manager protocol,
    allowing safe resource management:

        with workspace:
            workspace.execute_command("echo 'hello'")
    """

    working_dir: str = Field(
        description="The working directory for agent operations and tool execution."
    )

    def __enter__(self) -> "BaseWorkspace":
        """Enter the workspace context.

        Returns:
            Self for use in with statements
        """
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the workspace context and cleanup resources.

        Default implementation performs no cleanup. Subclasses should override
        to add cleanup logic (e.g., stopping containers, closing connections).

        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred
        """
        pass

    @abstractmethod
    def execute_command(
        self,
        command: str,
        cwd: str | Path | None = None,
        timeout: float = 30.0,
    ) -> CommandResult:
        """Execute a bash command on the system.

        Args:
            command: The bash command to execute
            cwd: Working directory for the command (optional)
            timeout: Timeout in seconds (defaults to 30.0)

        Returns:
            CommandResult: Result containing stdout, stderr, exit_code, and other
                metadata

        Raises:
            Exception: If command execution fails
        """
        ...

    @abstractmethod
    def file_upload(
        self,
        source_path: str | Path,
        destination_path: str | Path,
    ) -> FileOperationResult:
        """Upload a file to the system.

        Args:
            source_path: Path to the source file
            destination_path: Path where the file should be uploaded

        Returns:
            FileOperationResult: Result containing success status and metadata

        Raises:
            Exception: If file upload fails
        """
        ...

    @abstractmethod
    def file_download(
        self,
        source_path: str | Path,
        destination_path: str | Path,
    ) -> FileOperationResult:
        """Download a file from the system.

        Args:
            source_path: Path to the source file on the system
            destination_path: Path where the file should be downloaded

        Returns:
            FileOperationResult: Result containing success status and metadata

        Raises:
            Exception: If file download fails
        """
        ...
