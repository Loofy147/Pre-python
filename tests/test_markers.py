from chipcup.markers import MarkerPolicy, MarkerRow, evaluate_matrix


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
