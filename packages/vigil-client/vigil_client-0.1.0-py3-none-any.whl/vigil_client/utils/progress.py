"""Progress bar utilities for vigil-client."""

from __future__ import annotations

from typing import Optional

try:
    from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class ProgressBar:
    """Progress bar for upload/download operations."""

    def __init__(self, description: str = "Processing", total: Optional[int] = None):
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

    def __enter__(self):
        if self.progress:
            self.progress.start()
            self.task = self.progress.add_task(self.description, total=self.total)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.progress:
            self.progress.stop()

    def update(self, advance: int = 1):
        """Update progress."""
        if self.progress:
            self.progress.advance(self.task, advance)

    def set_total(self, total: int):
        """Set total progress."""
        if self.progress:
            self.progress.update(self.task, total=total)

    def set_description(self, description: str):
        """Set description."""
        if self.progress:
            self.progress.update(self.task, description=description)
