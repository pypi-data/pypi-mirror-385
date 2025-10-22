"""Progress bar utilities for vigil-client."""

from __future__ import annotations

try:
    from rich.progress import BarColumn, Progress, TextColumn, TimeRemainingColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class ProgressBar:
    """Progress bar for upload/download operations."""

    def __init__(self, description: str = "Processing", total: int | None = None):
        self.description = description
        self.total = total
        self.progress = None

        if RICH_AVAILABLE:
            self.progress = Progress(
                TextColumn("[bold blue]{task.description}"),
                BarColumn(),
                "[progress.percentage]{task.percentage:>3.0f}%",
                TimeRemainingColumn(),
            )

    def __enter__(self) -> "ProgressBar":
        if self.progress:
            self.progress.start()
            self.task = self.progress.add_task(self.description, total=self.total)
        return self

    def __exit__(self, _exc_type, _exc_val, _exc_tb) -> None:
        if self.progress:
            self.progress.stop()

    def update(self, advance: int = 1) -> None:
        """Update progress."""
        if self.progress:
            self.progress.advance(self.task, advance)

    def set_total(self, total: int) -> None:
        """Set total progress."""
        if self.progress:
            self.progress.update(self.task, total=total)

    def set_description(self, description: str) -> None:
        """Set description."""
        if self.progress:
            self.progress.update(self.task, description=description)
