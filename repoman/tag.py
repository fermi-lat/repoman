from git import Repo
import os

SCONS_SCRIPTS = ["SConscript", "SConstruct"]

class Tag:

    def __init__(self, package_path):
        self.package_path = package_path

    def tag(self, tag, note, branch=None, custom=None, scons_files=False):
        pass

    def do_git_tag(self, tag, notes, branch=None, release_tag=False, repo_path=None):
        """CvsTag::makeTag"""

        package_file = self._find_package_file()


    def latest_tag(self, filename):
        pass

    def _validate_tag(self, tag, custom):
        pass

    def _find_package_file(self):
        scons_file = None
        for scons in SCONS_SCRIPTS:
            scons_path = os.path.join(self.package_path, scons)
            if os.path.exists(scons_path):
                scons_file = scons_path
        if not scons_file:
            raise FileNotFoundError("No SCons file found for package")
        return scons_file
