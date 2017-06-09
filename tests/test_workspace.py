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
        req_path = os.path.join(self.working_path, "tip/cmt/requirements")
        with open(req_path, "w") as check_force_file:
            check_force_file.write("some garbage")
        try:
            self.workspace.checkout("tip", ref="eb92ec2")
            self.fail("Should have failed checkout")
        except Exception as e:
            pass

        try:
            self.workspace.checkout("tip", ref="eb92ec2", force=True)
        except Exception as e:
            self.fail("Should have not failed forced checkout")

    def test_checkout_packages(self):
        packages = [
            ("xmlBase", "xmlBase-05-07-01"),
            ("astro", "astro-04-00-02")
        ]
        self.workspace.checkout_packages(packages)

if __name__ == '__main__':
    unittest.main()
