import subprocess
from pathlib import Path


def test_multiline_output(tmp_path):
    playbook_src = Path("tests/fixtures/test_playbook.yml")
    playbook_dst = tmp_path / "test_playbook.yml"
    playbook_dst.write_text(playbook_src.read_text())

    cfg_file = tmp_path / "ansible.cfg"
    cfg_file.write_text("""
    [defaults]
    stdout_callback = gerreich.tools.default_with_clean_msg
    """)

    result = subprocess.run(
        ["ansible-playbook", str(playbook_dst)],
        cwd=tmp_path,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    out = result.stdout
    assert "Message Output" in out
    assert "Line 1" in out
    assert "Line 2" in out
    assert "Line 3" in out
