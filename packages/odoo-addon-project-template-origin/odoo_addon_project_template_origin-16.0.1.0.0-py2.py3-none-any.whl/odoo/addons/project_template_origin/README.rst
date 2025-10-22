================================
Project Template Origin
================================

This module extends the project management functionality by tracking the origin template
of projects that are created from templates.

Features
========

* **Template Origin Tracking**: Adds a ``project_template_id`` field to track which template a project was copied from
* **Automatic Template Reference**: When copying a project, the template origin is automatically preserved
* **Settings Tab Integration**: Displays the template origin in the project's settings tab as a read-only field

Technical Details
=================

Dependencies
------------

* ``project_template``: This module depends on the project_template module for template functionality

Models
------

Project
~~~~~~~

Extends ``project.project`` with:

* ``project_template_id`` (Many2one): Reference to the project template this project was copied from

Methods
-------

* ``copy()``: Overrides the copy method to preserve template origin when copying projects

Views
-----

* ``project.xml``: Adds the project_template_id field to the settings tab of the project form view

Installation
============

1. Ensure the ``project_template`` module is installed
2. Install this module through the Odoo interface or by adding it to your addons path

Usage
=====

1. Create a project and mark it as a template using the ``project_template`` module
2. Copy the project using the template functionality
3. The copied project will show the original template in the "Project Template Origin" field in the settings tab

Testing
=======

Run the test suite::

    python -m pytest project_template_origin/tests/

The module includes comprehensive tests covering:

* Template origin field functionality
* Project copying with template preservation
* Field access and display

License
=======

This module is licensed under the AGPL-3 license, same as the Odoo project_template module.

Authors
=======

* Som IT Cooperatiu SCCL
* Nicolás Ramos <nicolas.ramos@somit.coop>
