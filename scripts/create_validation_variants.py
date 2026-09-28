from pathlib import Path
import cv2

SOURCE = Path("samples/invoices/sample_invoice.png")
OUTPUT_DIR = Path("samples/degraded")

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    image = cv2.imread(str(SOURCE))

    if image is None:
        raise FileNotFoundError(
            f"Unable to read source image: {SOURCE}"
        )

    missing_number = image.copy()
    cv2.rectangle(
        missing_number,
        (650, 175),
        (750, 210),
        (255, 255, 255),
        thickness=-1,
    )
    cv2.imwrite(
        str(OUTPUT_DIR / "invoice_missing_number.png"),
        missing_number,
    )

    missing_date = image.copy()
    cv2.rectangle(
        missing_date,
        (640, 200),
        (750, 235),
        (255, 255, 255),
        thickness=-1,
    )
    cv2.imwrite(
        str(OUTPUT_DIR / "invoice_missing_date.png"),
        missing_date,
    )

    missing_total = image.copy()
    cv2.rectangle(
        missing_total,
        (630, 530),
        (760, 585),
        (255, 255, 255),
        thickness=-1,
    )
    cv2.imwrite(
        str(OUTPUT_DIR / "invoice_missing_total.png"),
        missing_total,
    )

    wrong_total = image.copy()
    cv2.rectangle(
        wrong_total,
        (630, 530),
        (760, 585),
        (255, 255, 255),
        thickness=-1,
    )

    cv2.putText(
        wrong_total,
        "$160.00",
        (650, 570),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (0, 0, 0),
        2,
        cv2.LINE_AA,
    )

    cv2.imwrite(
        str(OUTPUT_DIR / "invoice_wrong_total.png"),
        wrong_total,
    )

    print("Validation test variants created.")

if __name__ == "__main__":
    main()