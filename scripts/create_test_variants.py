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

    rotated = cv2.rotate(
        image,
        cv2.ROTATE_90_CLOCKWISE,
    )

    cv2.imwrite(
        str(OUTPUT_DIR / "invoice_rotated_90.png"),
        rotated,
    )

    height, width = image.shape[:2]

    low_resolution = cv2.resize(
        image,
        (
            max(1, width // 3),
            max(1, height // 3),
        ),
        interpolation=cv2.INTER_AREA,
    )

    cv2.imwrite(
        str(OUTPUT_DIR / "invoice_low_resolution.png"),
        low_resolution,
    )

    blurred = cv2.GaussianBlur(
        image,
        (5, 5),
        1.5,
    )

    cv2.imwrite(
        str(OUTPUT_DIR / "invoice_blurred.png"),
        blurred,
    )

    print("Created degraded test variants.")

if __name__ == "__main__":
    main()