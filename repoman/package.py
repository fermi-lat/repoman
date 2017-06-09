

def read_package_list(package_path):
    """
    Read the list of package requirements and version
    specifications (tags) into a list of lists.    
    :param package_path: Path to the packageList.txt file
    """
    package_specs = []
    with open(package_path, "r") as pfile:
        package_specs = read_package_list_file(pfile)
    return package_specs


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
        # ref can have no whitespace
        package_specs.append([package, ref])
    return package_specs
