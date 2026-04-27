from __future__ import annotations

import io
from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, StyleSheet1, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    Image as RLImage,
    KeepTogether,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from technical.report_channel import (
    ReportDocument,
    ReportFigureItem,
    ReportItem,
    ReportTableItem,
    ReportTextItem,
)

class ReportLabPdfExporter:

    def __init__(self):
        self._register_fonts()
        self._styles = self._build_styles()

    def export(self, document: ReportDocument, path: str) -> None:
        doc = SimpleDocTemplate(
            path,
            pagesize=A4,
            leftMargin=12 * mm,
            rightMargin=12 * mm,
            topMargin=12 * mm,
            bottomMargin=12 * mm,
            title=document.title,
            author="NodeProject",
        )

        story = self._build_story(document, doc.width)
        doc.build(
            story,
            onFirstPage=self._draw_page_number,
            onLaterPages=self._draw_page_number,
        )

    def _register_fonts(self) -> None:
        regular = self._find_font(
            [
                "DejaVuSans.ttf",
                "arial.ttf",
                "segoeui.ttf",
            ]
        )
        bold = self._find_font(
            [
                "DejaVuSans-Bold.ttf",
                "arialbd.ttf",
                "segoeuib.ttf",
            ]
        )
        italic = self._find_font(
            [
                "DejaVuSans-Oblique.ttf",
                "ariali.ttf",
                "segoeuii.ttf",
            ]
        )
        mono = self._find_font(
            [
                "DejaVuSansMono.ttf",
                "consola.ttf",
                "cour.ttf",
            ]
        )

        missing = []
        if regular is None:
            missing.append("regular")
        if bold is None:
            missing.append("bold")
        if italic is None:
            missing.append("italic")
        if mono is None:
            missing.append("mono")

        if missing:
            raise FileNotFoundError(
                "Не удалось найти подходящие TTF-шрифты для PDF-экспорта.\n\n"
                "Положи шрифты в assets/fonts или проверь наличие шрифтов в C:\\Windows\\Fonts.\n\n"
                "Поддерживаемые варианты:\n"
                "regular: DejaVuSans.ttf / arial.ttf / segoeui.ttf\n"
                "bold: DejaVuSans-Bold.ttf / arialbd.ttf / segoeuib.ttf\n"
                "italic: DejaVuSans-Oblique.ttf / ariali.ttf / segoeuii.ttf\n"
                "mono: DejaVuSansMono.ttf / consola.ttf / cour.ttf\n\n"
                f"Не найдены типы: {', '.join(missing)}"
            )

        self._register_font_once("AppRegular", regular)
        self._register_font_once("AppBold", bold)
        self._register_font_once("AppItalic", italic)
        self._register_font_once("AppMono", mono)

    def _find_font(self, filenames: list[str]) -> Path | None:
        search_dirs = [
            Path(__file__).resolve().parent.parent / "assets" / "fonts",
            Path(r"C:\Windows\Fonts"),
        ]

        for directory in search_dirs:
            if not directory.exists():
                continue
            for name in filenames:
                candidate = directory / name
                if candidate.exists():
                    return candidate

        return None

    @staticmethod
    def _register_font_once(font_name: str, font_path: Path) -> None:
        if font_name not in set(pdfmetrics.getRegisteredFontNames()):
            pdfmetrics.registerFont(TTFont(font_name, str(font_path)))

    def _build_styles(self) -> StyleSheet1:
        styles = getSampleStyleSheet()

        styles.add(
            ParagraphStyle(
                name="ReportTitle",
                parent=styles["Title"],
                fontName="AppBold",
                fontSize=20,
                leading=24,
                textColor=colors.HexColor("#111827"),
                spaceAfter=8,
                alignment=TA_LEFT,
            )
        )

        styles.add(
            ParagraphStyle(
                name="ReportSubtitle",
                parent=styles["Normal"],
                fontName="AppRegular",
                fontSize=10,
                leading=13,
                textColor=colors.HexColor("#6B7280"),
                spaceAfter=12,
            )
        )

        styles.add(
            ParagraphStyle(
                name="BlockTitle",
                parent=styles["Heading2"],
                fontName="AppBold",
                fontSize=13,
                leading=16,
                textColor=colors.HexColor("#111827"),
                spaceAfter=7,
                spaceBefore=0,
            )
        )

        styles.add(
            ParagraphStyle(
                name="Body",
                parent=styles["BodyText"],
                fontName="AppRegular",
                fontSize=10.2,
                leading=14,
                textColor=colors.HexColor("#1F2937"),
                spaceAfter=0,
            )
        )

        styles.add(
            ParagraphStyle(
                name="Caption",
                parent=styles["BodyText"],
                fontName="AppItalic",
                fontSize=9.2,
                leading=12,
                textColor=colors.HexColor("#4B5563"),
                alignment=TA_LEFT,
                spaceBefore=5,
            )
        )

        styles.add(
            ParagraphStyle(
                name="TableCell",
                parent=styles["BodyText"],
                fontName="AppRegular",
                fontSize=9,
                leading=11,
                textColor=colors.HexColor("#1F2937"),
            )
        )

        styles.add(
            ParagraphStyle(
                name="TableHeader",
                parent=styles["BodyText"],
                fontName="AppBold",
                fontSize=9,
                leading=11,
                textColor=colors.HexColor("#111827"),
            )
        )

        styles.add(
            ParagraphStyle(
                name="MonoBody",
                parent=styles["BodyText"],
                fontName="AppMono",
                fontSize=9.4,
                leading=12,
                textColor=colors.HexColor("#1F2937"),
            )
        )

        return styles

    def _build_story(self, document: ReportDocument, available_width: float) -> list:
        story: list = []

        story.append(
            Paragraph(self._xml_escape(document.title), self._styles["ReportTitle"])
        )
        if document.subtitle:
            story.append(
                Paragraph(
                    self._xml_escape(document.subtitle), self._styles["ReportSubtitle"]
                )
            )

        story.append(
            HRFlowable(
                width="100%",
                thickness=0.8,
                color=colors.HexColor("#D1D5DB"),
                spaceAfter=12,
                spaceBefore=0,
            )
        )

        for idx, item in enumerate(document.items):
            story.extend(self._item_to_flowables(item, available_width))
            if idx != len(document.items) - 1:
                story.append(Spacer(1, 8))

        return story

    def _item_to_flowables(self, item: ReportItem, available_width: float) -> list:
        if isinstance(item, ReportTextItem):
            return self._text_item_to_flowables(item, available_width)
        if isinstance(item, ReportTableItem):
            return self._table_item_to_flowables(item, available_width)
        if isinstance(item, ReportFigureItem):
            return self._figure_item_to_flowables(item, available_width)
        return []

    def _text_item_to_flowables(
        self, item: ReportTextItem, available_width: float
    ) -> list:
        parts: list = []

        if item.title:
            parts.append(
                Paragraph(self._xml_escape(item.title), self._styles["BlockTitle"])
            )

        pre = Preformatted(
            text=item.text or "",
            style=ParagraphStyle(
                "MonoPre",
                parent=self._styles["MonoBody"],
                fontName="AppMono",
                fontSize=9.4,
                leading=12,
                leftIndent=0,
                rightIndent=0,
                borderPadding=0,
            ),
            maxLineLength=max(60, int(available_width / 6.2)),
            splitChars=None,
        )
        parts.append(pre)

        return [KeepTogether(parts), self._bottom_rule()]

    def _table_item_to_flowables(
        self, item: ReportTableItem, available_width: float
    ) -> list:
        parts: list = []

        if item.title:
            parts.append(
                Paragraph(self._xml_escape(item.title), self._styles["BlockTitle"])
            )

        rows = [item.headers] + item.rows
        col_widths = self._compute_column_widths(rows, available_width)

        table_data = []
        for row_idx, row in enumerate(rows):
            styled_row = []
            for cell in row:
                style_name = "TableHeader" if row_idx == 0 else "TableCell"
                styled_row.append(
                    Paragraph(self._xml_escape(str(cell)), self._styles[style_name])
                )
            table_data.append(styled_row)

        tbl = Table(
            table_data,
            colWidths=col_widths,
            repeatRows=1,
            hAlign="LEFT",
        )
        tbl.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F3F4F6")),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#1F2937")),
                    ("GRID", (0, 0), (-1, -1), 0.6, colors.HexColor("#D1D5DB")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, colors.HexColor("#FAFAFA")],
                    ),
                ]
            )
        )

        parts.append(tbl)
        return parts + [self._bottom_rule()]

    def _figure_item_to_flowables(
        self, item: ReportFigureItem, available_width: float
    ) -> list:
        parts: list = []

        if item.title:
            parts.append(
                Paragraph(self._xml_escape(item.title), self._styles["BlockTitle"])
            )

        image_bytes = self._figure_to_png_bytes(item.figure)
        reader = ImageReader(io.BytesIO(image_bytes))
        img_w_px, img_h_px = reader.getSize()

        max_width = available_width
        max_height = 150 * mm

        draw_w = max_width
        draw_h = draw_w * (img_h_px / img_w_px)

        if draw_h > max_height:
            draw_h = max_height
            draw_w = draw_h * (img_w_px / img_h_px)

        img = RLImage(io.BytesIO(image_bytes), width=draw_w, height=draw_h)
        img.hAlign = "CENTER"
        parts.append(img)

        if item.caption:
            parts.append(Spacer(1, 4))
            parts.append(
                Paragraph(self._xml_escape(item.caption), self._styles["Caption"])
            )

        return [KeepTogether(parts), self._bottom_rule()]

    def _bottom_rule(self):
        return Spacer(1, 6)

    def _compute_column_widths(
        self, rows: list[list[str]], available_width: float
    ) -> list[float]:
        if not rows:
            return [available_width]

        num_cols = max(len(row) for row in rows)
        weights = [1.0] * num_cols

        for col_idx in range(num_cols):
            max_len = 1
            for row in rows:
                if col_idx < len(row):
                    max_len = max(max_len, len(str(row[col_idx])))
            weights[col_idx] = min(max(max_len, 8), 40)

        total = sum(weights)
        raw_widths = [(w / total) * available_width for w in weights]

        min_w = 22 * mm
        adjusted = [max(w, min_w) for w in raw_widths]

        total_adjusted = sum(adjusted)
        if total_adjusted > available_width:
            scale = available_width / total_adjusted
            adjusted = [w * scale for w in adjusted]

        return adjusted

    def _figure_to_png_bytes(self, fig) -> bytes:
        buf = io.BytesIO()
        fig.savefig(
            buf,
            format="png",
            dpi=220,
            bbox_inches="tight",
            facecolor="white",
            edgecolor="none",
        )
        return buf.getvalue()

    @staticmethod
    def _xml_escape(text: str) -> str:
        return escape(text or "").replace("\n", "<br/>")

    @staticmethod
    def _draw_page_number(canvas, doc) -> None:
        canvas.saveState()
        canvas.setFont("AppRegular", 9)
        canvas.setFillColor(colors.HexColor("#6B7280"))
        canvas.drawRightString(
            doc.pagesize[0] - doc.rightMargin,
            8 * mm,
            f"Стр. {canvas.getPageNumber()}",
        )
        canvas.restoreState()
