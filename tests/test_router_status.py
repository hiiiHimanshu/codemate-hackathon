from ui.render import format_status


def test_format_status_success():
    assert format_status("ok", 12.3456) == "✔ 12.35ms"


def test_format_status_failure():
    assert format_status("error", 0.0) == "✖ 0.00ms"
