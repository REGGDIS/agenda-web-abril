"""Pruebas de las rutas HTML generales."""

from backend.tests.conftest import get_client


def test_login_view_hides_authenticated_navigation_and_keeps_theme_toggle():
    client = get_client()

    response = client.get("/login")

    assert response.status_code == 200
    assert "Organiza y gestiona tus actividades del mes de abril" in response.text
    assert "data-theme-toggle" in response.text
    assert '<nav class="site-nav">' not in response.text
    assert "/actividades/nueva" not in response.text
    assert ">Inicio<" not in response.text
    assert ">Login<" not in response.text
    assert "Entrar al calendario" in response.text
    assert "corporate-memphis-agenda-abril.png" in response.text
    assert "login-illustration-panel" in response.text
    assert 'id="login-success-actions" class="login-success-actions" hidden' in response.text
