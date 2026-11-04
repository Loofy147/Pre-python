from chipcup.markers import MarkerPolicy, MarkerRow, evaluate_matrix
from chipcup.versions import VersionPolicy


def test_extra_marker_is_false_without_selected_extra():
    assert not MarkerPolicy('extra == "gpu"').evaluate()


def test_extra_marker_is_true_for_requested_extra():
    assert MarkerPolicy('extra == "gpu"', extras=("gpu",)).evaluate()


def test_matrix_logs_rows_and_selects_stub_sets():
    rows = (
        MarkerRow(
            "linux",
            "sys_platform == 'linux'",
            "posix",
            environment={"sys_platform": "linux"},
        ),
        MarkerRow(
            "gpu-extra",
            'extra == "gpu"',
            "gpu",
            extra="gpu",
        ),
        MarkerRow(
            "disabled",
            "python_version < '2.0'",
            "legacy",
        ),
    )
    result = evaluate_matrix(rows)
    assert result.selected_rows == ("linux", "gpu-extra")
    assert result.selected_stub_sets == ("posix", "gpu")
    assert result.evaluations[2].log_line == "marker-eval row=disabled result=False"



def test_version_floor_and_extra_select_the_protocol_contract():
    rows = (
        MarkerRow(
            "gpu-extra",
            'extra == "gpu"',
            "gpu",
            version_specifier=">=1.4",
            extra="gpu",
        ),
        MarkerRow(
            "legacy-gpu",
            'extra == "gpu"',
            "gpu",
            version_specifier="<1.4",
            extra="gpu",
        ),
    )
    scoped = VersionPolicy(">=1.4").select_matrix_rows("1.4.0", rows)
    matrix = evaluate_matrix(scoped)

    assert tuple(row.name for row in scoped) == ("gpu-extra",)
    assert matrix.selected_stub_sets == ("gpu",)

    from chipcup.types import load

    assert {contract.__name__ for contract in load(matrix.selected_stub_sets[0])} == {
        "AuditReceipt",
        "Reader",
    }
