import shutil
from pathlib import Path

from openhands.sdk.logger import get_logger
from openhands.sdk.utils.command import execute_command
from openhands.sdk.workspace.base import BaseWorkspace
from openhands.sdk.workspace.models import CommandResult, FileOperationResult


logger = get_logger(__name__)


class LocalWorkspace(BaseWorkspace):
    """Mixin providing local workspace operations."""

    def execute_command(
        self,
        command: str,
        cwd: str | Path | None = None,
        timeout: float = 30.0,
    ) -> CommandResult:
        """Execute a bash command locally.

        Uses the shared shell execution utility to run commands with proper
        timeout handling, output streaming, and error management.

        Args:
            command: The bash command to execute
            cwd: Working directory (optional)
            timeout: Timeout in seconds

        Returns:
            CommandResult: Result with stdout, stderr, exit_code, command, and
                timeout_occurred
        """
        logger.debug(f"Executing local bash command: {command} in {cwd}")
        result = execute_command(
            command,
            cwd=str(cwd) if cwd is not None else str(self.working_dir),
            timeout=timeout,
            print_output=True,
        )
        return CommandResult(
            command=command,
            exit_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            timeout_occurred=result.returncode == -1,
        )

    def file_upload(
        self,
        source_path: str | Path,
        destination_path: str | Path,
    ) -> FileOperationResult:
        """Upload (copy) a file locally.

        For local systems, file upload is implemented as a file copy operation
        using shutil.copy2 to preserve metadata.

        Args:
            source_path: Path to the source file
            destination_path: Path where the file should be copied

        Returns:
            FileOperationResult: Result with success status and file information
        """
        source = Path(source_path)
        destination = Path(destination_path)

        logger.debug(f"Local file upload: {source} -> {destination}")

        try:
            # Ensure destination directory exists
            destination.parent.mkdir(parents=True, exist_ok=True)

            # Copy the file with metadata preservation
            shutil.copy2(source, destination)

            return FileOperationResult(
                success=True,
                source_path=str(source),
                destination_path=str(destination),
                file_size=destination.stat().st_size,
            )

        except Exception as e:
            logger.error(f"Local file upload failed: {e}")
            return FileOperationResult(
                success=False,
                source_path=str(source),
                destination_path=str(destination),
                error=str(e),
            )

    def file_download(
        self,
        source_path: str | Path,
        destination_path: str | Path,
    ) -> FileOperationResult:
        """Download (copy) a file locally.

        For local systems, file download is implemented as a file copy operation
        using shutil.copy2 to preserve metadata.

        Args:
            source_path: Path to the source file
            destination_path: Path where the file should be copied

        Returns:
            FileOperationResult: Result with success status and file information
        """
        source = Path(source_path)
        destination = Path(destination_path)

        logger.debug(f"Local file download: {source} -> {destination}")

        try:
            # Ensure destination directory exists
            destination.parent.mkdir(parents=True, exist_ok=True)

            # Copy the file with metadata preservation
            shutil.copy2(source, destination)

            return FileOperationResult(
                success=True,
                source_path=str(source),
                destination_path=str(destination),
                file_size=destination.stat().st_size,
            )

        except Exception as e:
            logger.error(f"Local file download failed: {e}")
            return FileOperationResult(
                success=False,
                source_path=str(source),
                destination_path=str(destination),
                error=str(e),
            )
