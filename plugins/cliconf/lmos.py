# Copyright (c) 2025, Lantronix (<ansible@lantronix.com>)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
name: lmos
short_description: CLI interface for Lantronix LMOS devices
description:
  - Provides CLI command execution for Lantronix Local Manager OS (LMOS) devices
    over SSH using the C(ansible.netcommon.network_cli) connection plugin.
version_added: "1.0.0"
author:
  - Lantronix Product Team (@lantronix)
"""

EXAMPLES = r"""
- name: Run show version on an LMOS device
  vars:
    ansible_network_os: lantronix.lmos.lmos
    ansible_connection: ansible.netcommon.network_cli
  tasks:
    - name: Gather LMOS facts
      lantronix.lmos.lmos_facts:

    - name: Run a show command
      ansible.netcommon.cli_command:
        command: show system ip
      register: result
"""

import json
import re

from ansible.errors import AnsibleConnectionFailure
from ansible.module_utils._text import to_text
from ansible.module_utils.common._collections_compat import Mapping
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import to_list
from ansible_collections.ansible.netcommon.plugins.plugin_utils.cliconf_base import CliconfBase


class Cliconf(CliconfBase):

    def get(
        self,
        command=None,
        prompt=None,
        answer=None,
        sendonly=False,
        newline=True,
        output=None,
        check_all=False,
    ):
        if not command:
            raise ValueError("must provide value of command to execute")
        if output:
            raise ValueError("'output' value %s is not supported for get" % output)

        return self.send_command(
            command=command,
            prompt=prompt,
            answer=answer,
            sendonly=sendonly,
            newline=newline,
            check_all=check_all,
        )

    def run_commands(self, commands=None, check_rc=True):
        if commands is None:
            raise ValueError("'commands' value is required")

        responses = list()
        for cmd in to_list(commands):
            if not isinstance(cmd, Mapping):
                cmd = {"command": cmd}

            output = cmd.pop("output", None)
            if output:
                raise ValueError("'output' value %s is not supported for run_commands" % output)

            try:
                out = self.send_command(**cmd)
            except AnsibleConnectionFailure as e:
                if check_rc:
                    raise
                out = getattr(e, "err", to_text(e))

            responses.append(out)

        return responses

    def get_device_info(self):
        device_info = {}
        device_info["network_os"] = "lmos"

        try:
            reply = self.get(command="show ver\r\n")
            data = to_text(reply, errors="surrogate_or_strict").strip()
        except AnsibleConnectionFailure:
            return device_info

        match = re.search(r"LMOS version: (\S+)", data)
        if match:
            device_info["network_os_version"] = match.group(1)

        match = re.search(r"^Model: (.+)$", data, re.M)
        if match:
            device_info["network_os_model"] = match.group(1).strip()

        match = re.search(r"^Serial number: (\S+)$", data, re.M)
        if match:
            device_info["network_os_serial"] = match.group(1)

        try:
            reply = self.get(command="show system ip\r\n")
            ip_data = to_text(reply, errors="surrogate_or_strict").strip()
            match = re.search(r"^Host Name: (.+)$", ip_data, re.M)
            if match:
                device_info["network_os_hostname"] = match.group(1).strip()
        except AnsibleConnectionFailure:
            pass

        return device_info

    def get_device_operations(self):
        return {
            "supports_diff_replace": False,
            "supports_commit": False,
            "supports_rollback": False,
            "supports_defaults": False,
            "supports_onbox_diff": False,
            "supports_commit_comment": False,
            "supports_multiline_delimiter": False,
            "supports_diff_match": False,
            "supports_diff_ignore_lines": False,
            "supports_generate_diff": False,
            "supports_replace": False,
        }

    def get_option_values(self):
        return {
            "format": ["text"],
            "diff_match": [],
            "diff_replace": [],
            "output": [],
        }

    def get_capabilities(self):
        result = super(Cliconf, self).get_capabilities()
        result["rpc"] += ["run_commands"]
        result["device_operations"] = self.get_device_operations()
        result.update(self.get_option_values())
        return json.dumps(result)

    def set_cli_prompt_context(self):
        if self._connection.connected:
            out = self._connection.get_prompt()
            if out is None:
                raise AnsibleConnectionFailure(
                    message="cli prompt is not identified from the last received"
                    " response window: %s" % self._connection._last_recv_window,
                )
