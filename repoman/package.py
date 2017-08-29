
class Package:
    def __init__(self, workspace, repo, path):
        self.workspace = workspace
        self.repo = repo
        self.path = path


class PackageSpec:
    def __init__(self, name, ref=None, ref_path=None):
        self.name = name
        self.ref = ref
        self.ref_path = ref_path

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return repr(self.__dict__)