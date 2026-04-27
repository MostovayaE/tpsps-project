from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING, Union

from matplotlib.figure import Figure

if TYPE_CHECKING:
    import pandas as pd

@dataclass
class ReportTextItem:
    title: str | None
    text: str

@dataclass
class ReportTableItem:
    title: str | None
    headers: list[str]
    rows: list[list[str]]

@dataclass
class ReportFigureItem:
    title: str | None
    figure: Figure
    caption: str | None = None

ReportItem = Union[ReportTextItem, ReportTableItem, ReportFigureItem]

@dataclass
class ReportDocument:
    title: str = "Результаты пайплайна"
    subtitle: str | None = None
    items: list[ReportItem] = field(default_factory=list)

class ReportChannel:

    def __init__(self, document: Optional[ReportDocument] = None):
        if document is not None and not isinstance(document, ReportDocument):
            raise TypeError(
                "ReportChannel ожидает ReportDocument или None. "
                "Не передавай сюда FinalDialog."
            )

        self._document = document or ReportDocument()
        self._buffered = False
        self._buffer: list[ReportItem] = []
        self._lock = threading.Lock()

        self.wizard_opener = None

    @property
    def document(self) -> ReportDocument:
        return self._document

    def set_title(self, title: str, subtitle: str | None = None) -> None:
        self._document.title = title
        self._document.subtitle = subtitle

    def clear(self) -> None:
        self._document.items.clear()
        self._buffer.clear()
        self._buffered = False

    def enable_buffering(self) -> None:
        with self._lock:
            self._buffered = True

    def flush(self) -> None:
        with self._lock:
            self._document.items.extend(self._buffer)
            self._buffer.clear()
            self._buffered = False

    def _append(self, item: ReportItem) -> None:
        with self._lock:
            if self._buffered:
                self._buffer.append(item)
            else:
                self._document.items.append(item)

    def add_text(self, text: str, *, title: str | None = None) -> None:
        self._append(ReportTextItem(title=title, text=text))

    def add_figure(
        self,
        fig: Figure,
        *,
        title: str | None = None,
        caption: str | None = None,
    ) -> None:
        self._append(
            ReportFigureItem(
                title=title,
                figure=fig,
                caption=caption,
            )
        )

    def add_table(
        self,
        headers: list[str],
        rows: list[list[str]],
        *,
        title: str | None = None,
    ) -> None:
        normalized_headers = [str(h) for h in headers]
        normalized_rows = [[str(cell) for cell in row] for row in rows]
        self._append(
            ReportTableItem(
                title=title,
                headers=normalized_headers,
                rows=normalized_rows,
            )
        )
