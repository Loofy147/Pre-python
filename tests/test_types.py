from typing import Any

import pytest

from chipcup.types import AuditReceipt, is_any, prepare_build_receipt


class Receipt:
    source_digest = "b" * 64
    passed = True


def test_structural_receipt_is_accepted():
    assert isinstance(Receipt(), AuditReceipt)
    evidence = prepare_build_receipt(Receipt())
    assert evidence.passed
    assert evidence.source_digest == "b" * 64


def test_any_is_visible_as_escape_hatch():
    assert is_any(Any)
    assert not is_any(str)


def test_failed_receipt_cannot_cross_build_boundary():
    class FailedReceipt:
        source_digest = "b" * 64
        passed = False

    with pytest.raises(ValueError):
        prepare_build_receipt(FailedReceipt())
