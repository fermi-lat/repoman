
class Package:
    def __init__(self, name, workspace, repo, path):
        self.name = name
        self.workspace = workspace
        self.repo = repo
        self.path = path

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
