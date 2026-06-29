=========================================
Lantronix LMOS Collection Release Notes
=========================================

.. contents:: Topics

v1.0.1
======

Bugfixes
--------

- ``meta/runtime.yml`` -- bumped ``requires_ansible`` from ``>=2.15.0`` to ``>=2.16.0``
  to meet Red Hat Automation Hub certification requirement (AAP 2.4 lifecycle).
- ``galaxy.yml`` -- updated repository, documentation, and issues URLs to the official
  Lantronix GitHub organization (``github.com/Lantronix``).

v1.0.0
======

New Plugins
-----------

- ``lantronix.lmos.lmos`` terminal plugin -- handles LMOS ANSI escape sequences and prompt detection via SSH
- ``lantronix.lmos.lmos`` cliconf plugin -- provides CLI command interface for LMOS devices

New Modules
-----------

- ``lantronix.lmos.lmos_facts`` -- gather structured facts from an LMOS device (version, model, serial, hostname, management IP)
