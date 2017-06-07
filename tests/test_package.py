import unittest
from unittest import TestCase
from repoman.package import read_package_list
import os
import json

PACKAGELIST_FILES = ["packagelist_1.txt"]


class TestPackage(TestCase):

    def test_read_package_list(self):
        test_dir = os.path.dirname(__file__)
        for f in PACKAGELIST_FILES:
            package_path = os.path.join(test_dir, f)
            json_path = package_path + ".json"
            with open(json_path, "r") as json_file:
                expected = json.loads(json_file.read())
            actual = read_package_list(package_path)
            self.assertEqual(actual, expected, "list differs from expected")

if __name__ == '__main__':
    unittest.main()
