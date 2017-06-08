import unittest
from unittest import TestCase
from repoman import Workspace
import tempfile
import shutil
import os


class TestStage(TestCase):

    def setUp(self):
        self.working_path = tempfile.mkdtemp()
        self.workspace = Workspace(self.working_path)

    def tearDown(self):
        shutil.rmtree(self.working_path)

    def test_checkout(self):
        self.workspace.checkout("tip")
        self.workspace.checkout("tip")
        self.workspace.checkout("tip", ref="tags/v0")
        self.workspace.checkout("tip", ref="eb92ec2")

    def test_checkout_packages(self):
        packages = [
            ("xmlBase", "xmlBase-05-07-01"),
            ("astro", "astro-04-00-02")
        ]
        self.workspace.checkout_packages(packages)

if __name__ == '__main__':
    unittest.main()
