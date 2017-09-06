from git import Repo
from .error import RepomanError


class Package:
    def __init__(self, name, workspace, path, repo=None):
        self.name = name
        self.workspace = workspace
        self.path = path
        self.repo = repo or Repo(path)
        # FIXME: assert_valid_repo(self.repo)

    def read_manifest(self):
        from .manifest import find_manifest, read_manifest
        manifest_path = find_manifest(self.path)
        if not manifest_path:
            raise RepomanError("Package isn't a product")
        return read_manifest(manifest_path)

    def has_dependencies(self):
        from .manifest import find_manifest
        """
        A product is a special package which is collection of
        packages prepared together into a logical application.

        For Fermi, this includes ScienceTools and GlastRelease.
        """
        return find_manifest(self.path) is not None

    def describe(self):
        """
        Describe this package the most recent package tag.
        """
        # FIXME: Write this
        pass

    def describe_version(self):
        """
        Describe the version string based on the most recent tag.
        """
        # FIXME: Write this
        pass


class PackageSpec:
    def __init__(self, name, ref=None, ref_path=None):
        self.name = name
        self.ref = ref
        self.ref_path = ref_path

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return repr(self.__dict__)
