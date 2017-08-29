import unittest
from unittest import TestCase
from repoman.package import PackageSpec
from repoman.manifest import read_manifest, update_manifest
import os
import shutil
import json

PACKAGELIST_FILES = ["packagelist_1.txt"]


class TestPackage(TestCase):

    def tearDown(self):
        test_dir = os.path.dirname(__file__)
        p2_path = os.path.join(test_dir, "packagelist_2.txt")
        shutil.copy(p2_path + ".orig", p2_path)

    def test_read_package_list(self):
        test_dir = os.path.dirname(__file__)
        f = "packagelist_1.txt"
        manifest_path = os.path.join(test_dir, f)
        json_path = manifest_path + ".json"
        with open(json_path, "r") as json_file:
            expected = json.loads(json_file.read())
            expected = [PackageSpec(*spec_args) for spec_args in expected]
        actual = read_manifest(manifest_path)
        self.assertEqual(actual, expected, "list differs from expected")

    def test_write_package_list(self):
        test_dir = os.path.dirname(__file__)
        f = "packagelist_2.txt"
        manifest_path = os.path.join(test_dir, f)
        expected_path = manifest_path + ".expected"
        json_path = manifest_path + ".json"
        with open(json_path, "r") as json_file:
            spec_list = json.loads(json_file.read())
            new_specs = [PackageSpec(*spec_args) for spec_args in spec_list]
        update_manifest(manifest_path, new_specs)
        with open(manifest_path, "r") as actual_f:
            actual = actual_f.read()
        with open(expected_path, "r") as expected_f:
            expected = expected_f.read()
        self.assertEqual(actual, expected, "package list differs from expected")

if __name__ == '__main__':
    unittest.main()
