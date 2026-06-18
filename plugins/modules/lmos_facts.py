#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2025, Lantronix (<ansible@lantronix.com>)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: lmos_facts
short_description: Gather facts from a Lantronix LMOS device
version_added: "1.0.0"
author:
  - Lantronix Product Team (@lantronix)
description:
  - Connects to a Lantronix Local Manager OS (LMOS) device via SSH and gathers
    structured facts by parsing C(show ver) and C(show system ip) output.
  - Requires C(ansible_network_os=lantronix.lmos.lmos) and
    C(ansible_connection=ansible.netcommon.network_cli) in inventory.
notes:
  - No parameters are required. Facts are gathered automatically on module invocation.
  - The module is read-only and never changes device configuration.
"""

EXAMPLES = r"""
- name: Gather LMOS facts
  lantronix.lmos.lmos_facts:
  register: result

- name: Print LMOS version
  debug:
    msg: "Device is running LMOS {{ ansible_facts.lmos_facts.lmos_version }}"

- name: Assert minimum LMOS version
  assert:
    that:
      - ansible_facts.lmos_facts.lmos_version is version('6.7', '>=')
    fail_msg: "LMOS version too old: {{ ansible_facts.lmos_facts.lmos_version }}"
"""

RETURN = r"""
lmos_facts:
  description: Structured facts gathered from the LMOS device.
  returned: always
  type: dict
  contains:
    lmos_version:
      description: LMOS software version string.
      type: str
      sample: "6.7.0.44374"
    lmos_build:
      description: LMOS build timestamp.
      type: str
      sample: "20241217:010445"
    model:
      description: Hardware model identifier.
      type: str
      sample: "Virtual"
    serial_number:
      description: Device serial number.
      type: str
      sample: "V345678901"
    fips_mode:
      description: FIPS 140-2 mode status.
      type: str
      sample: "disabled"
    uptime:
      description: Device uptime string.
      type: str
      sample: "19h 22m"
    last_boot:
      description: Timestamp of last full boot.
      type: str
      sample: "12/17/24-14:29:25"
    hostname:
      description: Device hostname from C(show system ip). Empty string if unavailable.
      type: str
      sample: "v22-V345678901"
    management_ip:
      description: Management IP address from C(show system ip). Empty string if unavailable.
      type: str
      sample: "172.3.4.5"
"""

import re

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import Connection


def _parse_show_ver(output):
    facts = {
        "lmos_version": "",
        "lmos_build": "",
        "model": "",
        "serial_number": "",
        "fips_mode": "",
        "uptime": "",
        "last_boot": "",
    }

    patterns = {
        "lmos_version": r"LMOS version: (\S+)",
        "lmos_build": r"LMOS build: (\S+)",
        "model": r"^Model: (.+)$",
        "serial_number": r"^Serial number: (\S+)$",
        "fips_mode": r"^FIPS 140-2 mode: (.+)$",
        "uptime": r"^Uptime: (.+)$",
        "last_boot": r"^Last boot: (\S+)$",
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, output, re.M)
        if match:
            facts[key] = match.group(1).strip()

    return facts


def _parse_show_system_ip(output):
    result = {"hostname": "", "management_ip": ""}

    match = re.search(r"^Host Name: (.+)$", output, re.M)
    if match:
        result["hostname"] = match.group(1).strip()

    match = re.search(r"^Management IP: (\S+)$", output, re.M)
    if match:
        result["management_ip"] = match.group(1).strip()

    return result


def main():
    module = AnsibleModule(
        argument_spec=dict(),
        supports_check_mode=True,
    )

    connection = Connection(module._socket_path)

    try:
        ver_output = connection.run_commands(["show ver\r\n"])[0]
    except Exception as exc:
        module.fail_json(msg="Failed to run 'show ver': %s" % str(exc))
        return

    facts = _parse_show_ver(ver_output)

    try:
        ip_output = connection.run_commands(["show system ip\r\n"])[0]
        facts.update(_parse_show_system_ip(ip_output))
    except Exception:
        facts.update({"hostname": "", "management_ip": ""})

    module.exit_json(changed=False, ansible_facts={"lmos_facts": facts})


if __name__ == "__main__":
    main()
