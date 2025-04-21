import os
import pytest


@pytest.fixture
def fake_result(mocker):
    def _make(msg="Hello\nWorld", changed=True, status="changed"):
        result = mocker.MagicMock()
        result._result = {"msg": msg}
        if changed:
            result._result["changed"] = True

        result.is_changed.return_value = (status == "changed")
        result.is_skipped.return_value = (status == "skipped")
        result.is_failed.return_value = (status == "failed")
        result.is_unreachable.return_value = (status == "unreachable")

        task = mocker.MagicMock()
        task._uuid = "task-123"
        task.get_name.return_value = "Mocked Task"
        task.check_mode = False
        task.no_log = False
        task.args = {}
        result._task = task

        return result

    return _make


@pytest.fixture
def ansible_config_with_callback(tmp_path, monkeypatch):
    """
    Creates a temp ansible.cfg pointing to the custom callback plugin.
    Sets ANSIBLE_CONFIG to use it.
    """
    callback_dir = os.path.abspath("plugins/callback")
    config_path = tmp_path / "ansible.cfg"

    config_path.write_text(f"""
[defaults]
stdout_callback = default_with_clean_msg
callback_plugins = {callback_dir}
""")

    monkeypatch.setenv("ANSIBLE_CONFIG", str(config_path))
    yield config_path  # Optional if you want to check content later
