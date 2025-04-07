from ansible.plugins.callback.default import CallbackModule as DefaultCallback
from ansible.utils.display import Display
from ansible import constants as C

DOCUMENTATION = '''
    name: default_with_clean_msg
    type: stdout
    short_description: Default callback with clean multiline msg support
    version_added: "custom"
    description:
        - Subclass of the default callback plugin that prints msg values as boxed multiline output.
    extends_documentation_fragment:
      - default_callback
      - result_format_callback
'''

class CallbackModule(DefaultCallback):

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'default_with_clean_msg'

    def _get_result_color(self, result):
        if result.is_changed():
            return C.COLOR_CHANGED
        if result.is_skipped():
            return C.COLOR_SKIP
        if result.is_unreachable():
            return C.COLOR_UNREACHABLE
        if result.is_failed():
            return C.COLOR_ERROR
        return C.COLOR_OK
    
    def _is_only_msg(self, result):
        # These are keys we want to ignore for the purpose of "message-only" detection
        internal_keys = {
            'changed',
            'invocation',
            'deprecations',
            'warnings',
            '_ansible_verbose_always',
            '_ansible_no_log',
            '_ansible_item_label',
            '_ansible_parsed',
            '_ansible_ignore_errors',
            '_ansible_item_result',
            '_ansible_item_loop_var'
        }

        # Get only user-facing keys
        keys = [k for k in result._result.keys() if k not in internal_keys and not k.startswith('_')]
        return keys == ['msg']

    def _print_clean_msg(self, result, color=None):
        if color is None:
            color = C.COLOR_CHANGED if result._result.get('changed', False) else C.COLOR_OK

        msg_body = result._result.get('msg')
        if isinstance(msg_body, str) and msg_body.strip():
            lines = msg_body.strip().splitlines()
            max_len = max(len(line) for line in lines) + 1
            label = " Message Output "

            is_too_short = len(label) >= max_len
            if is_too_short:
                max_len = len(label) + 8

            prefix = "=" * ((max_len - len(label)) // 2)
            suffix = "=" * ((max_len - len(label) + 1) // 2)

            border = "=" * max_len
            label_border = prefix + label + suffix
            
            self._display.display(f"\n{label_border}", color=color)
            for line in lines:
                self._display.display(line, color=color)
            self._display.display(f"{border}\n", color=color)

    def v2_runner_on_ok(self, result):
        is_changed = result._result.get('changed', False)
        has_only_msg = self._is_only_msg(result)

        # Suppress default verbose JSON output if we already show it cleanly
        if not has_only_msg or self._display.verbosity >= 2:
            super().v2_runner_on_ok(result)
        else:
            host_label = self.host_label(result)
            msg = "changed" if is_changed else "ok"
            self._display.display(f"{msg}: [{host_label}]", color=self._get_result_color(result))

        self._print_clean_msg(result, color=self._get_result_color(result))

    def v2_runner_on_failed(self, result, ignore_errors=False):
        super().v2_runner_on_failed(result, ignore_errors)
        self._print_clean_msg(result, color=C.COLOR_ERROR)

    def v2_runner_on_skipped(self, result):
        super().v2_runner_on_skipped(result)
        self._print_clean_msg(result, color=C.COLOR_SKIP)
