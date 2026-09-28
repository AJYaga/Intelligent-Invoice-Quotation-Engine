from decimal import Decimal
from app.services.extraction.utils import parse_decimal

def test_parse_plain_decimal():
    assert parse_decimal("450.00") == Decimal("450.00")

def test_parse_currency_symbol():
    assert parse_decimal("$450") == Decimal("450")

def test_parse_currency_with_comma():
    assert parse_decimal("$1,100.50") == Decimal("1100.50")

def test_parse_currency_code():
    assert parse_decimal("LKR 1250.00") == Decimal("1250.00")

def test_parse_parenthesized_negative():
    assert parse_decimal("(50.00)") == Decimal("-50.00")

def test_parse_invalid_number():
    assert parse_decimal("not-a-number") is None