from __future__ import absolute_import, division, print_function
__metaclass__ = type

from unittest.mock import patch, MagicMock
from ansible_collections.lantronix.lmos.plugins.modules import lmos_facts


SHOW_VER_OUTPUT = """\
All Rights Reserved. Lantronix and its respective logos are trademarks of
Lantronix, Inc. in the United States and other jurisdictions.

Model: Virtual
Serial number: V345678901
LMOS version: 6.7.0.44374
LMOS build: 20241217:010445
FIPS 140-2 mode: disabled

Secondary Ethernet: supported
Uptime: 19h 22m
Last boot: 12/17/24-14:29:25
Last incremental restart: 12/17/24-20:33:46
"""

SHOW_SYSTEM_IP_OUTPUT = """\
Use DHCP: Yes
Management IP: 172.3.4.5
Host Name: v22-V345678901
Subnet Mask: 255.255.255.0
Broadcast Address: 172.3.4.255
Default Route: 172.3.4.254
"""


def _make_module_mock(params=None):
    m = MagicMock()
    m.params = params or {}
    m.check_mode = False
    m._socket_path = "/tmp/fake.socket"
    return m


def test_success_path():
    with patch("ansible_collections.lantronix.lmos.plugins.modules.lmos_facts.AnsibleModule") as mock_mod_cls:
        with patch("ansible_collections.lantronix.lmos.plugins.modules.lmos_facts.Connection") as mock_conn_cls:
            m = _make_module_mock()
            mock_mod_cls.return_value = m

            conn = MagicMock()
            conn.run_commands.side_effect = [
                [SHOW_VER_OUTPUT],
                [SHOW_SYSTEM_IP_OUTPUT],
            ]
            mock_conn_cls.return_value = conn

            lmos_facts.main()

            kwargs = m.exit_json.call_args[1]
            assert kwargs["changed"] is False
            facts = kwargs["ansible_facts"]["lmos_facts"]
            assert facts["lmos_version"] == "6.7.0.44374"
            assert facts["lmos_build"] == "20241217:010445"
            assert facts["model"] == "Virtual"
            assert facts["serial_number"] == "V345678901"
            assert facts["fips_mode"] == "disabled"
            assert facts["uptime"] == "19h 22m"
            assert facts["last_boot"] == "12/17/24-14:29:25"
            assert facts["hostname"] == "v22-V345678901"
            assert facts["management_ip"] == "172.3.4.5"


def test_show_system_ip_failure_is_graceful():
    with patch("ansible_collections.lantronix.lmos.plugins.modules.lmos_facts.AnsibleModule") as mock_mod_cls:
        with patch("ansible_collections.lantronix.lmos.plugins.modules.lmos_facts.Connection") as mock_conn_cls:
            m = _make_module_mock()
            mock_mod_cls.return_value = m

            conn = MagicMock()
            conn.run_commands.side_effect = [
                [SHOW_VER_OUTPUT],
                Exception("connection lost"),
            ]
            mock_conn_cls.return_value = conn

            lmos_facts.main()

            kwargs = m.exit_json.call_args[1]
            facts = kwargs["ansible_facts"]["lmos_facts"]
            assert facts["lmos_version"] == "6.7.0.44374"
            assert facts["hostname"] == ""
            assert facts["management_ip"] == ""


def test_show_ver_failure_calls_fail_json():
    with patch("ansible_collections.lantronix.lmos.plugins.modules.lmos_facts.AnsibleModule") as mock_mod_cls:
        with patch("ansible_collections.lantronix.lmos.plugins.modules.lmos_facts.Connection") as mock_conn_cls:
            m = _make_module_mock()
            mock_mod_cls.return_value = m

            conn = MagicMock()
            conn.run_commands.side_effect = Exception("SSH timeout")
            mock_conn_cls.return_value = conn

            lmos_facts.main()

            assert m.fail_json.called
            kwargs = m.fail_json.call_args[1]
            assert "show ver" in kwargs["msg"]
            assert "SSH timeout" in kwargs["msg"]


def test_missing_fields_return_empty_strings():
    with patch("ansible_collections.lantronix.lmos.plugins.modules.lmos_facts.AnsibleModule") as mock_mod_cls:
        with patch("ansible_collections.lantronix.lmos.plugins.modules.lmos_facts.Connection") as mock_conn_cls:
            m = _make_module_mock()
            mock_mod_cls.return_value = m

            conn = MagicMock()
            conn.run_commands.side_effect = [
                ["LMOS version: 6.5.0.12345\n"],
                [""],
            ]
            mock_conn_cls.return_value = conn

            lmos_facts.main()

            kwargs = m.exit_json.call_args[1]
            facts = kwargs["ansible_facts"]["lmos_facts"]
            assert facts["lmos_version"] == "6.5.0.12345"
            assert facts["model"] == ""
            assert facts["serial_number"] == ""
            assert facts["hostname"] == ""
