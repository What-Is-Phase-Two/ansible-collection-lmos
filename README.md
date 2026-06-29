# lantronix.lmos, Ansible Collection

Ansible collection for Lantronix **LMOS** (Local Manager OS) devices, including the Uplogix Local Manager product line. Provides SSH CLI connectivity without requiring `ansible_network_terminal_errors: ignore`.

## Requirements

- Ansible Core >= 2.16 (see [Compatibility Note](#compatibility-note))
- `ansible.netcommon` >= 5.0.0
- SSH access to LMOS devices on port 22

## Installation

### From Ansible Automation Hub (recommended)

> Install with:
>
> ```bash
> ansible-galaxy collection install lantronix.lmos
> ```

### From GitHub

Clone the repository into the required Ansible collections directory structure. The path `ansible_collections/lantronix/lmos/` is required for `ansible-test` and namespace resolution to work correctly.

```bash
mkdir -p ~/ansible_collections/lantronix
git clone https://github.com/Lantronix/ansible-collection-lmos \
    ~/ansible_collections/lantronix/lmos
```

Install the collection dependency:

```bash
ansible-galaxy collection install "ansible.netcommon>=5.0.0"
```

Add the collections path to your `ansible.cfg` or set the environment variable:

```ini
# ansible.cfg
[defaults]
collections_path = ~/ansible_collections
```

Or:

```bash
export ANSIBLE_COLLECTIONS_PATH=~/ansible_collections:~/.ansible/collections
```

### Build and install from source tarball

```bash
cd ~/ansible_collections/lantronix/lmos
ansible-galaxy collection build
ansible-galaxy collection install lantronix-lmos-1.0.0.tar.gz
```

## Inventory Configuration

```yaml
# inventory.yml
all:
  hosts:
    lm-device-01:
      ansible_host: 192.168.1.100
      ansible_user: admin
      ansible_ssh_pass: "{{ vault_lmos_password }}"
      ansible_port: 22
      ansible_connection: ansible.netcommon.network_cli
      ansible_network_os: lantronix.lmos.lmos
      ansible_become: false
```

## Modules

| Module | Description |
|--------|-------------|
| `lantronix.lmos.lmos_facts` | Gather structured facts from an LMOS device |

## Plugins

| Plugin | Type | Description |
|--------|------|-------------|
| `lantronix.lmos.lmos` | terminal | Handles LMOS ANSI escape sequences and prompt detection |
| `lantronix.lmos.lmos` | cliconf | CLI command interface for LMOS devices |

## Usage

### Gather facts

```yaml
- name: Gather LMOS device facts
  hosts: all
  gather_facts: false

  tasks:
    - lantronix.lmos.lmos_facts:

    - ansible.builtin.debug:
        msg: "{{ inventory_hostname }} is running LMOS {{ ansible_facts.lmos_facts.lmos_version }}"
```

**Returns:**

| Fact | Description | Example |
|------|-------------|---------|
| `lmos_version` | LMOS software version | `6.8.0.45000` |
| `lmos_build` | Build date/timestamp | `20250101:120000` |
| `model` | Hardware model | `LM4` |
| `serial_number` | Device serial number | `A810100093` |
| `fips_mode` | FIPS mode status | `disabled` |
| `uptime` | Device uptime string | `22h 43m` |
| `last_boot` | Last boot timestamp | `06/01/25-09:00:00` |
| `hostname` | Management hostname | `core-lm-01` |
| `management_ip` | Management IP address | `192.168.1.100` |

### Run show commands

```yaml
- name: Run show commands on LMOS devices
  hosts: all
  gather_facts: false

  tasks:
    - name: Get system IP configuration
      ansible.netcommon.cli_command:
        command: "show system ip\r\n"
      register: result

    - ansible.builtin.debug:
        var: result.stdout_lines
```

### IQOQ Validation

The included reference playbook implements a full IQOQ (Installation/Operational Qualification) run for compliance validation. It checks LMOS version, authentication, UCC management server, NTP, and syslog configuration.

```bash
ansible-playbook -i inventory.yml playbooks/iqoq_validate.yml \
  -e "expected_lmos_version=6.7" \
  -e "expected_ucc_host=uplogix-control-center.example.com" \
  -e "expected_ntp_server=ntp.example.com" \
  -e "expected_syslog_server=192.168.1.50"
```

All variables have safe defaults (empty string = skip that assertion). See `playbooks/iqoq_validate.yml` for the full parameter list.

## Background

LMOS emits ANSI escape sequences (`\x1b[0m`) at the end of every CLI output line. Without the custom terminal plugin in this collection, Ansible's standard networking plugins fail to detect the command prompt, causing connections to hang. The common workaround, `ansible_network_terminal_errors: ignore`, suppresses errors that may be real failures.

This collection fixes the problem cleanly. The `lantronix.lmos.lmos` terminal plugin extends `TerminalBase.ansi_re` to strip the ANSI reset sequence before prompt detection. No error suppression required.

## Compatibility Note

`ansible.netcommon` through version 8.5.3 calls `ActionBase._parse_returned_data()` with the pre-2.20 signature, which raises a `TypeError` at runtime under ansible-core 2.20. Until `ansible.netcommon` ships a fix, use **ansible-core 2.19.x**.

Tested against: ansible-core 2.16+ through 2.19.x, ansible.netcommon 8.5.3, Python 3.12.

## Testing

### Unit tests

```bash
cd ~/ansible_collections/lantronix/lmos
ansible-test units --python 3.12
```

### Sanity tests

```bash
ansible-test sanity --python 3.12
```

### Live device tests

Requires network access to an LMOS device. Edit `tests/live/inventory.yml` with your device details, then:

```bash
ansible-playbook -i tests/live/inventory.yml tests/live/test_lmos_live.yml
ansible-playbook -i tests/live/inventory.yml tests/live/test_serial_port.yml
```

## Support

This collection is maintained by the Lantronix OOB product team.

**Red Hat Automation Hub users:** Open a support request via the [collection page on Automation Hub](https://console.redhat.com/ansible/automation-hub/repo/published/lantronix/lmos) using the "Create issue" link. This ensures your request is routed through the appropriate Red Hat support channels.

**Community support:** Open an issue on [GitHub](https://github.com/Lantronix/ansible-collection-lmos/issues). Pull requests are welcome, please open an issue before submitting a PR for significant changes.

**Product support:** Visit [https://www.lantronix.com/support/](https://www.lantronix.com/support/).

## License

Apache-2.0. See [LICENSE](LICENSE).

Plugin and module files are licensed under GPL-3.0-or-later per Ansible module standards.
