from decimal import Decimal
from statistics import median
from app.models.extraction import LineItem
from app.models.ocr import OCRLine, OCRResult
from app.services.extraction.utils import normalize_text, parse_decimal

class LineItemExtractor:
    DESCRIPTION_HEADERS = ("description", "item", "product", "service")
    QUANTITY_HEADERS = ("qty", "quantity")
    PRICE_HEADERS = ("unit price", "price", "rate")
    TOTAL_HEADERS = ("amount", "line total", "total")

    def extract(self, ocr_result: OCRResult) -> list[LineItem]:
        items = []

        for page in ocr_result.pages:
            rows = self._group_into_rows(page.lines)
            header_index, columns = self._find_header(rows)

            if header_index is None or columns is None:
                continue

            for row in rows[header_index + 1:]:
                row_text = " ".join(line.text for line in row)
                normalized = normalize_text(row_text)

                if self._is_summary_row(normalized):
                    break

                item = self._parse_row(row, columns)

                if item is not None:
                    items.append(item)

        return items

    def _group_into_rows(
        self,
        lines: list[OCRLine],
    ) -> list[list[OCRLine]]:
        if not lines:
            return []

        heights = [
            max(point[1] for point in line.box.points)
            - min(point[1] for point in line.box.points)
            for line in lines
        ]

        tolerance = max(8.0, median(heights) * 0.7)

        ordered = sorted(
            lines,
            key=lambda line: (
                self._center_y(line),
                self._center_x(line),
            ),
        )

        rows: list[list[OCRLine]] = []

        for line in ordered:
            center_y = self._center_y(line)

            matched_row = None

            for row in rows:
                row_y = sum(
                    self._center_y(existing)
                    for existing in row
                ) / len(row)

                if abs(center_y - row_y) <= tolerance:
                    matched_row = row
                    break

            if matched_row is None:
                rows.append([line])
            else:
                matched_row.append(line)

        for row in rows:
            row.sort(key=self._center_x)

        rows.sort(
            key=lambda row: sum(
                self._center_y(line)
                for line in row
            ) / len(row)
        )

        return rows

    def _find_header(
        self,
        rows: list[list[OCRLine]],
    ) -> tuple[int | None, dict[str, OCRLine] | None]:
        for index, row in enumerate(rows):
            columns: dict[str, OCRLine] = {}

            for line in row:
                text = normalize_text(line.text)

                if self._matches_any(text, self.DESCRIPTION_HEADERS):
                    columns["description"] = line
                elif self._matches_any(text, self.QUANTITY_HEADERS):
                    columns["quantity"] = line
                elif self._matches_any(text, self.PRICE_HEADERS):
                    columns["unit_price"] = line
                elif self._matches_any(text, self.TOTAL_HEADERS):
                    columns["line_total"] = line

            required = {
                "description",
                "line_total",
            }

            if required.issubset(columns):
                return index, columns

        return None, None

    def _parse_row(
        self,
        row: list[OCRLine],
        columns: dict[str, OCRLine],
    ) -> LineItem | None:
        assigned = {
            name: []
            for name in columns
        }

        ordered_columns = sorted(
            columns.items(),
            key=lambda item: self._center_x(item[1]),
        )

        boundaries = []

        for index in range(len(ordered_columns) - 1):
            current_line = ordered_columns[index][1]
            next_line = ordered_columns[index + 1][1]

            boundary = (
                self._right(current_line)
                + self._left(next_line)
            ) / 2

            boundaries.append(boundary)

        for line in row:
            x = self._center_x(line)
            column_index = 0

            while (
                column_index < len(boundaries)
                and x >= boundaries[column_index]
            ):
                column_index += 1

            column_name = ordered_columns[column_index][0]
            assigned[column_name].append(line)

        description = " ".join(
            line.text
            for line in assigned.get(
                "description",
                [],
            )
        ).strip()

        if not description:
            return None

        quantity = self._parse_column_number(
            assigned.get("quantity", [])
        )

        unit_price = self._parse_column_number(
            assigned.get("unit_price", [])
        )

        line_total = self._parse_column_number(
            assigned.get("line_total", [])
        )

        if (
            quantity is None
            and unit_price is None
            and line_total is None
        ):
            return None

        confidence_values = [
            line.confidence
            for lines in assigned.values()
            for line in lines
        ]

        confidence = (
            sum(confidence_values)
            / len(confidence_values)
            if confidence_values
            else 0.0
        )

        return LineItem(
            description=description,
            quantity=quantity,
            unit_price=unit_price,
            line_total=line_total,
            confidence=round(confidence, 3),
        )

    @staticmethod
    def _parse_column_number(
        lines: list[OCRLine],
    ) -> Decimal | None:
        if not lines:
            return None

        text = "".join(line.text for line in lines)
        return parse_decimal(text)

    @staticmethod
    def _is_summary_row(text: str) -> bool:
        return any(
            label in text
            for label in (
                "subtotal",
                "sub total",
                "grand total",
                "amount due",
                "tax",
                "vat",
            )
        )

    @staticmethod
    def _matches_any(
        text: str,
        candidates: tuple[str, ...],
    ) -> bool:
        return any(candidate == text for candidate in candidates)

    @staticmethod
    def _center_x(line: OCRLine) -> float:
        return sum(
            point[0]
            for point in line.box.points
        ) / len(line.box.points)

    @staticmethod
    def _center_y(line: OCRLine) -> float:
        return sum(
            point[1]
            for point in line.box.points
        ) / len(line.box.points)
    
    @staticmethod
    def _left(line: OCRLine) -> float:
        return min(
            point[0]
            for point in line.box.points
        )

    @staticmethod
    def _right(line: OCRLine) -> float:
        return max(
            point[0]
            for point in line.box.points
        )