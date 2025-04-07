import pytest
from .utils import run_playbook

@pytest.mark.parametrize("task_block, expect_box, expect_color", [
    (
        '''
        - name: clean msg only
          debug:
            msg: |
              One
              Two
        ''',
        True,
        "ok"
    ),
    (
        '''
        - name: msg with other key
          debug:
            msg: Hello
          register: foo
        ''',
        False,
        "ok"
    ),
    (
        '''
        - name: empty msg
          debug:
            msg: ""
        ''',
        False,
        "ok"
    ),
    (
        '''
        - name: fail with multiline
          fail:
            msg: |
              Bad
              Error
          ignore_errors: true
        ''',
        True,
        "fatal"
    ),
    (
        '''
        - name: skipped task
          debug:
            msg: Skipped
          when: false
        ''',
        True,
        "skipping"
    ),
])
def test_box_behavior(task_block, expect_box, expect_color):
    playbook = f'''
    - name: Test task
      hosts: localhost
      gather_facts: false
      tasks:
        {task_block}
    '''
    output = run_playbook(playbook)
    
    if expect_box:
        assert "Message Output" in output
        assert "===" in output
    else:
        assert "Message Output" not in output

    assert expect_color in output
