

def read_package_list(package_path):
    package_specs = []
    with open(package_path, "r") as pfile:
        for line in pfile.readlines():
            # Strip comments
            line = line.split("#")[0]
            line = line.rstrip()
            if not len(line):
                continue
            (package, ref) = line.split(" ")
            # ref can have no whitespace
            package_specs.append([package, ref])
    return package_specs
