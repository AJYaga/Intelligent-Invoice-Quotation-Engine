from app.models.ocr import OCRLine

def left(line: OCRLine) -> float:
    return min(point[0] for point in line.box.points)

def right(line: OCRLine) -> float:
    return max(point[0] for point in line.box.points)

def top(line: OCRLine) -> float:
    return min(point[1] for point in line.box.points)

def bottom(line: OCRLine) -> float:
    return max(point[1] for point in line.box.points)

def center_x(line: OCRLine) -> float:
    return (left(line) + right(line)) / 2

def center_y(line: OCRLine) -> float:
    return (top(line) + bottom(line)) / 2

def height(line: OCRLine) -> float:
    return bottom(line) - top(line)

def find_value_to_right(
    label: OCRLine,
    lines: list[OCRLine],
    max_vertical_distance: float | None = None,
) -> OCRLine | None:
    tolerance = max_vertical_distance or max(15.0, height(label))

    candidates = []

    for candidate in lines:
        if candidate is label:
            continue

        if left(candidate) <= right(label):
            continue

        vertical_distance = abs(
            center_y(candidate) - center_y(label)
        )

        if vertical_distance > tolerance:
            continue

        horizontal_distance = left(candidate) - right(label)

        candidates.append(
            (
                vertical_distance,
                horizontal_distance,
                candidate,
            )
        )

    if not candidates:
        return None

    candidates.sort(
        key=lambda item: (
            item[0],
            item[1],
        )
    )

    return candidates[0][2]

def find_lines_below(
    label: OCRLine,
    lines: list[OCRLine],
    max_distance: float = 100.0,
    horizontal_margin: float = 120.0,
) -> list[OCRLine]:
    results = []

    label_x = center_x(label)

    for candidate in lines:
        if candidate is label:
            continue

        if top(candidate) < bottom(label):
            continue

        vertical_distance = (
            top(candidate) - bottom(label)
        )

        if vertical_distance > max_distance:
            continue

        if abs(
            center_x(candidate) - label_x
        ) > horizontal_margin:
            continue

        results.append(candidate)

    return sorted(
        results,
        key=lambda item: top(item),
    )

def find_value_below(
    label: OCRLine,
    lines: list[OCRLine],
    max_vertical_distance: float = 80.0,
) -> OCRLine | None:
    candidates = []

    label_left = left(label)
    label_right = right(label)
    label_center = center_x(label)

    for candidate in lines:
        if candidate is label:
            continue

        if top(candidate) < bottom(label):
            continue

        vertical_distance = top(candidate) - bottom(label)

        if vertical_distance > max_vertical_distance:
            continue

        candidate_center = center_x(candidate)

        horizontally_aligned = (
            label_left <= candidate_center <= label_right
            or abs(candidate_center - label_center) <= 60
        )

        if not horizontally_aligned:
            continue

        candidates.append(
            (
                vertical_distance,
                abs(candidate_center - label_center),
                candidate,
            )
        )

    if not candidates:
        return None

    candidates.sort(
        key=lambda item: (
            item[0],
            item[1],
        )
    )

    return candidates[0][2]