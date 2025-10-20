"""Custom Rich components with copy-friendly defaults."""

from __future__ import annotations

from rich import box
from rich.panel import Panel
from rich.table import Table


class AIPPanel(Panel):
    """Rich Panel configured without vertical borders by default."""

    def __init__(self, *args, **kwargs):
        """Initialize AIPPanel with default settings for horizontal borders and padding.

        Args:
            *args: Positional arguments passed to Panel
            **kwargs: Keyword arguments passed to Panel
        """
        kwargs.setdefault("box", box.HORIZONTALS)
        kwargs.setdefault("padding", (0, 1))
        super().__init__(*args, **kwargs)


class AIPTable(Table):
    """Rich Table configured without vertical borders by default."""

    def __init__(self, *args, **kwargs):
        """Initialize AIPTable with default settings for horizontal borders and no edge padding.

        Args:
            *args: Positional arguments passed to Table
            **kwargs: Keyword arguments passed to Table
        """
        kwargs.setdefault("box", box.HORIZONTALS)
        kwargs.setdefault("show_edge", False)
        kwargs.setdefault("pad_edge", False)
        super().__init__(*args, **kwargs)


class AIPGrid(Table):
    """Table-based grid with GL AIP defaults for layout blocks."""

    def __init__(
        self,
        *,
        expand: bool = True,
        padding: tuple[int, int] = (0, 1),
        collapse_padding: bool = True,
    ):
        """Initialize AIPGrid with zero-edge borders and optional expansion.

        Args:
            expand: Whether the grid should expand to fill available width.
            padding: Cell padding for the grid (row, column).
            collapse_padding: Collapse padding between renderables.
        """
        super().__init__(
            show_header=False,
            show_edge=False,
            pad_edge=False,
            box=None,
            expand=expand,
            padding=padding,
            collapse_padding=collapse_padding,
        )


__all__ = ["AIPPanel", "AIPTable", "AIPGrid"]
