import unittest
from unittest import TestCase
from repoman.workspace import Workspace
from repoman.tag import Tag
import tempfile
import shutil
import os


class TestStage(TestCase):

    def setUp(self):
        self.working_path = tempfile.mkdtemp()
        self.workspace = Workspace(self.working_path)

    def tearDown(self):
        shutil.rmtree(self.working_path)

    def test_tag(self):
        self.workspace.checkout("astro", "master")
        self.tagger = Tag(os.path.join(self.working_path, "astro"))
        #self.tagger.tag(tag, note=None, branch=None, custom=None, scons_files=None)