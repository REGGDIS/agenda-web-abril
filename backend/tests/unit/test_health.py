"""Prueba minima de salud del backend."""

from backend.tests.conftest import get_client


def test_healthcheck_returns_ok():
    client = get_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"

