from git import Repo, GitCommandError
from .error import RepomanError
import logging

logger = logging.getLogger(__name__)

DESCRIBE_MATCH_PATTERN = "{name}-[0-9][0-9]-[0-9][0-9]-[0-9][0-9]*"


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
        return self.repo.git.describe(
            "--dirty",
            "--match", DESCRIBE_MATCH_PATTERN.format(name=self.name),
            "--tags",
            "--always"
        )

    def closest_tag(self):
        """
        Describe this package the most recent package tag.
        """
        self.repo.commit()
        try:
            return self.repo.git.describe(
                "--match", DESCRIBE_MATCH_PATTERN.format(name=self.name),
                "--tags",
                "--abbrev=0"
            )
        except GitCommandError as e:
            logger.warning(e)
        return None


class PackageSpec:
    def __init__(self, name, ref=None, ref_path=None):
        self.name = name
        self.ref = ref
        self.ref_path = ref_path

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return repr(self.__dict__)
