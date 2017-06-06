import unittest
from unittest import TestCase
from repoman.stage import Stage
import tempfile
import shutil
import os


class TestStage(TestCase):

    def setUp(self):
        self.working_path = tempfile.mkdtemp()
        self.stage = Stage(self.working_path)

    def tearDown(self):
        shutil.rmtree(self.working_path)

    def test_checkout(self):
        self.stage.checkout("tip")
        self.stage.checkout("tip")
        self.stage.checkout("tip", ref="tags/v0")
        self.stage.checkout("tip", ref="eb92ec2")

    def test_checkout_packages(self):
        packages = [
            ("xmlBase", "xmlBase-05-07-01"),
            ("astro", "astro-04-00-02")
        ]
        self.stage.checkout_packages(packages)
        print(self.working_path)
        print(os.listdir(self.working_path))

if __name__ == '__main__':
    unittest.main()
