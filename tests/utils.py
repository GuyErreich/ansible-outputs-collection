import subprocess
from pathlib import Path

def run_playbook(playbook_str: str, callback: str = "gerreich.tools.default_with_clean_msg") -> str:
    tmp = Path.cwd() / ".test_run"
    tmp.mkdir(exist_ok=True)
    
    (tmp / "test.yml").write_text(playbook_str)
    (tmp / "ansible.cfg").write_text(f"[defaults]\nstdout_callback = {callback}\n")

    result = subprocess.run(
        ["ansible-playbook", "test.yml"],
        cwd=tmp,
        capture_output=True,
        text=True,
    )
    return result.stdout
