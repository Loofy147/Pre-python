from typing import Any

import pytest

from chipcup.types import (
    AuditReceipt,
    BuildEvidence,
    Reader,
    audit_stub_sets,
    is_any,
    prepare_build_receipt,
)


class Receipt:
    source_digest = "b" * 64
    passed = True


def test_structural_receipt_is_accepted_and_handed_to_build():
    receipt = Receipt()
    assert isinstance(receipt, AuditReceipt)
    evidence = prepare_build_receipt(receipt)
    assert isinstance(evidence, BuildEvidence)
    assert evidence.passed
    assert evidence.source_digest == "b" * 64


def test_any_is_detectable_as_an_explicit_escape_hatch():
    assert is_any(Any)
    assert not is_any(str)


def test_failed_receipt_cannot_cross_build_boundary():
    class FailedReceipt:
        source_digest = "b" * 64
        passed = False

    with pytest.raises(ValueError):
        prepare_build_receipt(FailedReceipt())


def test_generic_reader_declares_covariance():
    parameters = Reader.__parameters__
    assert len(parameters) == 1
    assert parameters[0].__covariant__


def test_marker_matrix_stub_set_names_are_checked():
    assert audit_stub_sets(("base", "posix", "gpu")) == ()
    assert audit_stub_sets(("unknown",)) == ("unknown",)
