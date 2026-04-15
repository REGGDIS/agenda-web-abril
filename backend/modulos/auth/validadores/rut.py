"""Validador de RUT basado en modulo 11."""

from __future__ import annotations

import re


RUT_PATTERN = re.compile(r"^\d{1,8}-[\dK]$")


class RutValidationError(ValueError):
    """Error controlado para validaciones de RUT."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def normalize_rut(rut: str) -> str:
    """Normaliza el RUT a formato canonico sin puntos y con guion."""

    cleaned_rut = rut.strip().upper().replace(".", "").replace(" ", "")
    if not cleaned_rut:
        return ""

    if "-" not in cleaned_rut and len(cleaned_rut) >= 2:
        cleaned_rut = f"{cleaned_rut[:-1]}-{cleaned_rut[-1]}"

    return cleaned_rut


def calculate_verifier_digit(rut_body: str) -> str:
    """Calcula el digito verificador usando modulo 11."""

    total = 0
    multiplier = 2

    for digit in reversed(rut_body):
        total += int(digit) * multiplier
        multiplier = 2 if multiplier == 7 else multiplier + 1

    remainder = 11 - (total % 11)
    if remainder == 11:
        return "0"
    if remainder == 10:
        return "K"
    return str(remainder)


def validate_rut_or_raise(rut: str) -> str:
    """Valida formato y digito verificador, devolviendo el RUT normalizado."""

    normalized_rut = normalize_rut(rut)
    if not normalized_rut:
        raise RutValidationError("empty_rut", "El RUT es obligatorio.")

    if not RUT_PATTERN.fullmatch(normalized_rut):
        raise RutValidationError(
            "invalid_format",
            "El RUT debe tener formato valido, por ejemplo 12.345.678-5.",
        )

    rut_body, provided_verifier = normalized_rut.split("-")
    expected_verifier = calculate_verifier_digit(rut_body)

    if expected_verifier != provided_verifier:
        raise RutValidationError(
            "invalid_verifier",
            "El digito verificador del RUT no es valido segun modulo 11.",
        )

    return normalized_rut
