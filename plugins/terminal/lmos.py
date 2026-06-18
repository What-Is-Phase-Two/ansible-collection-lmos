from __future__ import absolute_import, division, print_function
__metaclass__ = type

import re

from ansible.errors import AnsibleConnectionFailure
from ansible.utils.display import Display
from ansible_collections.ansible.netcommon.plugins.plugin_utils.terminal_base import TerminalBase

display = Display()


class TerminalModule(TerminalBase):
    terminal_stdout_re = [
        re.compile(rb"[\r\n]?\[[^]]+]# $"),
    ]

    # LMOS emits \x1b[0m (ANSI reset) at the end of every output line.
    # Without this extension the terminal plugin never detects the prompt.
    ansi_re = TerminalBase.ansi_re + [
        re.compile(rb"\x1b\[0m"),
    ]

    terminal_stderr_re = [
        re.compile(rb"% ?Error"),
        re.compile(rb"ERROR:", re.IGNORECASE),
        re.compile(rb"invalid input", re.I),
        re.compile(rb"connection timed out", re.I),
        re.compile(rb"[^\r\n]+ not found"),
    ]

    def on_open_shell(self):
        try:
            self._exec_cli_command(b"page-length 9999")
        except AnsibleConnectionFailure:
            display.display("WARNING: Unable to set terminal page length")
