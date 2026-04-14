"""Fixtures basicas para pruebas del backend."""

from fastapi.testclient import TestClient

from backend.app.main.app import app


def get_client() -> TestClient:
    return TestClient(app)

