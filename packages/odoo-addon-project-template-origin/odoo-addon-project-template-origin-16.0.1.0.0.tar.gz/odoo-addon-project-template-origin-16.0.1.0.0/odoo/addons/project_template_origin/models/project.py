# Copyright 2025 Som IT Cooperatiu SCCL - Nicolás Ramos <nicolas.ramos@somit.coop>
from odoo import api, fields, models


class Project(models.Model):
    """Extend project model to track template origin."""

    _inherit = "project.project"

    # Field to track the template origin of a project copy
    project_template_id = fields.Many2one(
        "project.project",
        string="Project Template",
        help="Reference to the project template this project was copied from",
        copy=True,
        readonly=True,
    )

    def create_project_from_template(self):
        """Override to set project_template_id when creating project from template."""
        # Store the template ID before creating the project
        template_id = self.id

        # Call parent method to create the project
        result = super(Project, self).create_project_from_template()

        # Get the newly created project from the action result
        if result and result.get('res_id'):
            new_project = self.env['project.project'].browse(result['res_id'])
            if new_project.exists():
                # Set the template origin reference
                new_project.project_template_id = template_id

        return result
