"""Pruebas del validador de RUT."""

import pytest

from backend.modulos.auth.validadores.rut import (
    RutValidationError,
    calculate_verifier_digit,
    normalize_rut,
    validate_rut_or_raise,
)


def test_normalize_rut_returns_canonical_format():
    assert normalize_rut(" 12.345.678-5 ") == "12345678-5"


def test_calculate_verifier_digit_supports_numeric_and_k_results():
    assert calculate_verifier_digit("12345678") == "5"
    assert calculate_verifier_digit("6") == "K"


def test_validate_rut_or_raise_accepts_valid_rut():
    assert validate_rut_or_raise("12.345.678-5") == "12345678-5"


@pytest.mark.parametrize(
    ("rut", "code"),
    [
        ("", "empty_rut"),
        ("abc", "invalid_format"),
        ("12.345.678-9", "invalid_verifier"),
    ],
)
def test_validate_rut_or_raise_rejects_invalid_inputs(rut: str, code: str):
    with pytest.raises(RutValidationError) as exc_info:
        validate_rut_or_raise(rut)

    assert exc_info.value.code == code
