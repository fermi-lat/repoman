from git import Repo
from .error import RepomanError
from .manifest import find_manifest, read_manifest


class Package:
    def __init__(self, name, workspace, path, repo=None):
        self.name = name
        self.workspace = workspace
        self.path = path
        self.repo = repo or Repo(path)
        # FIXME: assert_valid_repo(self.repo)

    def read_manifest(self):
        manifest_path = find_manifest(self.path)
        if not manifest_path:
            raise RepomanError("Package isn't a product")
        return read_manifest(manifest_path)

    def has_dependencies(self):
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

    # FIXME: Write this
    # def find_latest_tag(self):
    #     tags = self.repo.tags
    #
    # def find_head_tag(self):
    #     tags = self.repo.tags
    #
    # def find_last(self):
    #     head_pattern = re.compile(self.name + '-HEAD-1-\d*:')
    #     tags = self.repo.tags
    #     heads = [tag.name for tag in tags if re.findall(head_pattern, tag.name)]
    #     if not heads:
    #         logger.error("no match found")
    #         return ""
    #
    #     nhead = 0
    #     for h in heads:
    #         mobj = self.numPat.search(h)
    #         if int(mobj.group(1)) > nhead:
    #             nhead = int(mobj.group(1))
    #     return self.name + '-HEAD-1-' + str(nhead)



class PackageSpec:
    def __init__(self, name, ref=None, ref_path=None):
        self.name = name
        self.ref = ref
        self.ref_path = ref_path

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return repr(self.__dict__)
