# lantronix.lmos, Ansible Collection

Ansible collection for Lantronix **LMOS** (Local Manager OS) devices, including the Uplogix Local Manager product line.

## Requirements

- Ansible Core >= 2.14, < 2.20 (see note below)
- `ansible.netcommon` >= 5.0.0 (`ansible-galaxy collection install ansible.netcommon`)
- SSH access to LMOS devices on port 22

> **Note: ansible-core 2.20 compatibility.** `ansible.netcommon` through 8.5.3 calls
> `ActionBase._parse_returned_data()` with the pre-2.20 signature, which causes a
> `TypeError` at runtime. Until `ansible.netcommon` ships a fix, use ansible-core 2.19.x.
> Tested against ansible-core 2.19.10.

## Installation

```bash
ansible-galaxy collection install lantronix.lmos
```

Or from source:

```bash
git clone https://github.com/Lantronix/ansible-collection-lmos \
    ansible_collections/lantronix/lmos
cd ansible_collections/lantronix/lmos
ansible-galaxy collection install -r requirements.txt
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
  vars:
    ansible_connection: ansible.netcommon.network_cli
    ansible_network_os: lantronix.lmos.lmos

  tasks:
    - lantronix.lmos.lmos_facts:

    - debug:
        msg: "{{ inventory_hostname }} is running LMOS {{ ansible_facts.lmos_facts.lmos_version }}"
```

### Run show commands

```yaml
- name: Run show commands
  ansible.netcommon.cli_command:
    command: "show system ip\r\n"
  register: result

- debug:
    var: result.stdout_lines
```

### IQOQ Validation

The included reference playbook implements a full IQOQ qualification run:

```bash
ansible-playbook -i 192.168.1.100, playbooks/iqoq_validate.yml \
  -e "expected_lmos_version=6.7" \
  -e "expected_ucc_host=uplogix-control-center.example.com"
```

See `playbooks/iqoq_validate.yml` for the full parameter list.

## Background

LMOS emits ANSI escape sequences (`\x1b[0m`) at the end of every CLI output line. Without the custom terminal plugin in this collection, Ansible's standard networking plugins fail to detect the command prompt, causing connections to hang or error. This collection fixes the problem cleanly without requiring `ansible_network_terminal_errors: ignore`.

## License

Apache-2.0. See [LICENSE](LICENSE).
