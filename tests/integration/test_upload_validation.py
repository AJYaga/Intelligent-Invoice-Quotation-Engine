from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_valid_png_upload():
    response = client.post(
        "/api/documents/validate-upload",
        files={
            "file": (
                "sample.png",
                b"fake-image-content",
                "image/png",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["filename"] == "sample.png"
    assert data["extension"] == ".png"
    assert data["valid"] is True

def test_unsupported_file_extension():
    response = client.post(
        "/api/documents/validate-upload",
        files={
            "file": (
                "notes.txt",
                b"hello",
                "text/plain",
            )
        },
    )

    assert response.status_code == 415

def test_empty_file_rejected():
    response = client.post(
        "/api/documents/validate-upload",
        files={
            "file": (
                "empty.pdf",
                b"",
                "application/pdf",
            )
        },
    )
    assert response.status_code == 400