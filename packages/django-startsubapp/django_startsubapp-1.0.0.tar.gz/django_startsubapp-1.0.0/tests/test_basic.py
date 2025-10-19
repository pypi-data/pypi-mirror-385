"""
Basic tests for django-startsubapp package
Author: Saman Naruee <samannaruee@gmail.com>
"""
import os
import shutil
import tempfile
from unittest import TestCase
from django.core.management import call_command
from django.test import override_settings
from io import StringIO


class StartSubappCommandTest(TestCase):
    """Test cases for the startsubapp command"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()

    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_command_creates_app_in_apps_folder(self):
        """Test that command creates app in apps/ folder"""
        os.chdir(self.temp_dir)
        os.makedirs("apps", exist_ok=True)

        out = StringIO()
        call_command("startsubapp", "testapp", stdout=out)

        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "apps", "testapp")))

    def test_command_rejects_dots_in_app_name(self):
        """Test that command rejects app names with dots"""
        os.chdir(self.temp_dir)
        os.makedirs("apps", exist_ok=True)

        with self.assertRaises(Exception):
            call_command("startsubapp", "test.app")

    def test_app_has_init_file(self):
        """Test that created app has __init__.py"""
        os.chdir(self.temp_dir)
        os.makedirs("apps", exist_ok=True)

        call_command("startsubapp", "testapp")

        init_file = os.path.join(self.temp_dir, "apps", "testapp", "__init__.py")
        self.assertTrue(os.path.exists(init_file))

    def test_app_has_models_file(self):
        """Test that created app has models.py"""
        os.chdir(self.temp_dir)
        os.makedirs("apps", exist_ok=True)

        call_command("startsubapp", "testapp")

        models_file = os.path.join(self.temp_dir, "apps", "testapp", "models.py")
        self.assertTrue(os.path.exists(models_file))
