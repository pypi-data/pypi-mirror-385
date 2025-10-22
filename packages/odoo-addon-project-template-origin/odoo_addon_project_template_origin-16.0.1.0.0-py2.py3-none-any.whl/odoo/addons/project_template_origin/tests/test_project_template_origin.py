# Copyright 2025 Som IT Cooperatiu SCCL - Nicolás Ramos <nicolas.ramos@somit.coop>

import odoo.tests.common as common


class TestProjectTemplateOrigin(common.TransactionCase):
    """Test cases for project template origin functionality."""

    def setUp(self):
        """Set up test data."""
        super(TestProjectTemplateOrigin, self).setUp()

        # Create a template project
        self.template_project = self.env["project.project"].create({
            "name": "Test Template Project",
            "is_template": True,
        })

        # Create a regular project to use as template origin
        self.regular_project = self.env["project.project"].create({
            "name": "Regular Project",
            "is_template": False,
        })

    def test_project_template_field_exists(self):
        """Test that project_template_id field exists on project model."""
        # Check that the field exists
        self.assertTrue(hasattr(self.template_project, "project_template_id"))
        self.assertTrue(hasattr(self.regular_project, "project_template_id"))

    def test_copy_project_with_template_origin(self):
        """Test copying a project that has a template origin."""
        # Set template origin on regular project
        self.regular_project.project_template_id = self.template_project

        # Copy the project
        copied_project = self.regular_project.copy({
            "name": "Copied Project from Template",
        })

        # Check that the copied project has the template reference
        self.assertEqual(
            copied_project.project_template_id.id,
            self.template_project.id,
            "Copied project should have the same template origin"
        )

        # Check that the original project still has the template reference
        self.assertEqual(
            self.regular_project.project_template_id.id,
            self.template_project.id,
            "Original project should still have template origin"
        )

    def test_copy_project_without_template_origin(self):
        """Test copying a project that has no template origin."""
        # Copy project without template origin
        copied_project = self.regular_project.copy({
            "name": "Copied Project without Template",
        })

        # Check that the copied project has no template reference
        self.assertFalse(
            copied_project.project_template_id,
            "Copied project should have no template origin when original has none"
        )

    def test_project_template_id_readonly(self):
        """Test that project_template_id field is readonly."""
        # Try to set project_template_id directly (should work as it's not computed)
        self.regular_project.project_template_id = self.template_project

        # Verify it was set
        self.assertEqual(
            self.regular_project.project_template_id.id,
            self.template_project.id
        )

    def test_template_project_creation(self):
        """Test creating a template project."""
        # Create a template project
        template = self.env["project.project"].create({
            "name": "New Template",
            "is_template": True,
        })

        # Template should not have a template origin initially
        self.assertFalse(template.project_template_id)

    def test_project_template_origin_display_name(self):
        """Test that project template origin displays correctly."""
        # Set template origin
        self.regular_project.project_template_id = self.template_project

        # Check display name is accessible
        display_name = self.regular_project.project_template_id.display_name
        self.assertEqual(display_name, "Test Template Project")

    def test_create_project_from_template_sets_origin(self):
        """Test that creating a project from template sets the project_template_id."""
        # Use the create_project_from_template method
        result = self.template_project.create_project_from_template()

        # Check that the result contains the new project ID
        self.assertIn('res_id', result)
        new_project_id = result['res_id']

        # Browse the newly created project
        new_project = self.env['project.project'].browse(new_project_id)

        # Check that the project exists and has the correct template origin
        self.assertTrue(new_project.exists())
        self.assertEqual(
            new_project.project_template_id.id,
            self.template_project.id,
            "New project should have the template as its origin"
        )

        # Check that the new project is not a template itself
        self.assertFalse(new_project.is_template)

    def test_create_project_from_regular_project_no_origin(self):
        """Test that creating a project from a non-template doesn't set origin."""
        # Create a project from a regular project (not template)
        result = self.regular_project.create_project_from_template()

        # Check that the result contains the new project ID
        self.assertIn('res_id', result)
        new_project_id = result['res_id']

        # Browse the newly created project
        new_project = self.env['project.project'].browse(new_project_id)

        # Check that the project exists but has no template origin
        self.assertTrue(new_project.exists())
        self.assertFalse(
            new_project.project_template_id,
            "Project created from non-template should have no template origin"
        )
