import pytest
from plugins.callback.default_with_clean_msg import CallbackModule, C


def test_is_only_msg_true(fake_result):
    plugin = CallbackModule()
    result = fake_result(msg="just a message", status="ok")
    assert plugin._is_only_msg(result) is True


def test_is_only_msg_false(fake_result):
    plugin = CallbackModule()
    result = fake_result(msg="message", status="changed")
    result._result["extra"] = "something"
    assert plugin._is_only_msg(result) is False


@pytest.mark.parametrize("status, expected_color", [
    ("ok", C.COLOR_OK),
    ("changed", C.COLOR_CHANGED),
    ("failed", C.COLOR_ERROR),
    ("skipped", C.COLOR_SKIP),
    ("unreachable", C.COLOR_UNREACHABLE),
])
def test_result_color(fake_result, status, expected_color):
    plugin = CallbackModule()
    result = fake_result(status=status)
    assert plugin._get_result_color(result) == expected_color


def test_print_clean_msg_box_formatting(fake_result, mocker):
    plugin = CallbackModule()
    plugin._display = mocker.MagicMock()

    result = fake_result(msg="Line A\nLine B", status="changed")
    plugin._print_clean_msg(result)

    calls = [c.args[0] for c in plugin._display.display.call_args_list]
    assert any("Line A" in c for c in calls)
    assert any("Line B" in c for c in calls)
    assert any("Message Output" in c or "====" in c for c in calls)


def test_only_msg_suppresses_verbose_output(fake_result, mocker):
    plugin = CallbackModule()
    plugin._display = mocker.MagicMock()

    result = fake_result(msg="hello", status="ok")
    plugin._display.verbosity = 0

    plugin.v2_runner_on_ok(result)

    display_calls = [c.args[0] for c in plugin._display.display.call_args_list]
    assert any("Message Output" in c for c in display_calls)
    assert not any("=>" in c for c in display_calls)  # no JSON dump


def test_verbose_mode_includes_json_output(fake_result, mocker):
    plugin = CallbackModule()
    plugin._display = mocker.MagicMock()

    result = fake_result(msg="hello", status="ok")
    plugin._display.verbosity = 2

    plugin.v2_runner_on_ok(result)

    display_calls = [c.args[0] for c in plugin._display.display.call_args_list]
    assert any("=>" in c for c in display_calls)


def test_clean_msg_empty(fake_result, mocker):
    plugin = CallbackModule()
    plugin._display = mocker.MagicMock()

    result = fake_result(msg="", status="ok")
    plugin._print_clean_msg(result)

    # No calls expected since msg is empty
    assert plugin._display.display.call_count == 0
