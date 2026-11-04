from chipcup.markers import MarkerPolicy


def test_extra_marker_uses_selected_extra():
    policy = MarkerPolicy('extra == "fast"', extras=("slow", "fast"))
    assert policy.evaluate()


def test_marker_admission_hands_off_to_protocol_check():
    from chipcup.types import AuditReceipt

    class Receipt:
        source_digest = "a" * 64
        passed = True

    assert MarkerPolicy('python_version >= "3.10"').admits(Receipt(), AuditReceipt)
    assert not MarkerPolicy('python_version < "3.10"').admits(Receipt(), AuditReceipt)
