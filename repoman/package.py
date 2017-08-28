
class PackageSpec:
    def __init__(self, package, ref=None, ref_path=None):
        self.package = package
        self.ref = ref
        self.ref_path = ref_path

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


def read_package_list(package_path):
    """
    Read the list of package requirements and version
    specifications (tags) into a list of lists.    
    :param package_path: Path to the packageList.txt file
    """
    with open(package_path, "r") as pfile:
        return read_package_list_file(pfile)


def read_package_list_file(package_file):
    """
    Read the list of package requirements and version
    specifications (tags) into a list of lists.    
    :param package_file: package file
    """
    package_specs = []
    for line in package_file.readlines():
        # Strip comments
        line = line.split("#")[0]
        line = line.rstrip()
        if not len(line):
            continue
        (package, ref) = line.split(" ")
        ref_path = None
        if "/" in package:
            parts = package.split("/")
            package = parts[0]
            ref_path = "/".join(parts[1:])
        # ref can have no whitespace
        package_specs.append(PackageSpec(package, ref, ref_path))
    return package_specs
