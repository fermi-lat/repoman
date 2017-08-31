import os
from .package import PackageSpec
import logging

logger = logging.getLogger(__name__)

PACKAGE_LIST = "packageList.txt"


def find_manifest(package_dir):
    if PACKAGE_LIST in os.listdir(package_dir):
        return os.path.join(package_dir, PACKAGE_LIST)
    return None


def read_manifest(manifest_path):
    """
    Read the list of name requirements and version
    specifications (tags) into a list of lists.
    :param manifest_path: Path to the packageList.txt file
    """
    with open(manifest_path, "r") as pfile:
        return read_manifest_file(pfile)


def read_manifest_file(manifest_file):
    """
    Read the list of name requirements and version
    specifications (tags) into a list of lists.
    :param manifest_file: name file
    :returns List of :py:class:PackageSpec
    """
    package_specs = []
    for line in manifest_file.readlines():
        # Strip comments
        line = line.split("#")[0]
        line = line.rstrip()
        if not len(line):
            continue
        package_specs.append(get_spec(line))
    return package_specs


def update_manifest(manifest_path, package_specs):
    """
    Read the list of name requirements and version
    specifications (tags) into a list of lists.
    :param manifest_path: Path to the packageList.txt file
    :param package_specs: List of package specs to update manifest with
    """
    with open(manifest_path, "r+") as pfile:
        return update_manifest_file(pfile, package_specs)


def update_manifest_file(manifest_file, package_specs):
    """
    Read the list of current requirements and version
    specifications (tags) into a list of lists.
    :param manifest_file: name file
    :param package_specs: List of package specs to update manifest with
    """
    new_specs = {_mangle_spec(spec):spec for spec in package_specs}
    lines = [line for line in manifest_file.readlines()]
    new_lines = []
    for orig in lines:
        # Strip comments
        line_and_comment = orig.split("#")
        line = line_and_comment[0]
        comment = ""
        if len(line_and_comment) > 1:
            comment = "#".join(line_and_comment[1:]).rstrip()
        line = line.rstrip()

        if not len(line):
            # preserve whitespace
            new_lines.append(orig)
            continue

        old_spec = get_spec(line)
        mangled = _mangle_spec(old_spec)
        if mangled in new_specs and old_spec != new_specs[mangled]:
            new_spec = new_specs[mangled]
            line = format_spec(new_spec, comment)
            new_lines.append(line + "\n")
            del new_specs[mangled]
            logger.info("Updating spec for package: {}".format(mangled))
        elif mangled in new_specs:
            new_lines.append(orig)
            del new_specs[mangled]
            logger.info("Package unchanged: {}".format(old_spec.name))

    # Process new specs last
    unused_specs = [i for i in package_specs if i in new_specs.values()]
    for spec in unused_specs:
        logger.info("Writing new spec for package: {}".format(spec.name))
        new_lines.append(format_spec(spec) + "\n")
    manifest_file.seek(0)
    manifest_file.truncate()
    manifest_file.writelines(new_lines)


def _mangle_spec(spec):
    package = spec.name
    if spec.ref_path:
        package = '/'.join([package, spec.ref_path])
    return package


def format_spec(spec, comment=None):
    package = _mangle_spec(spec)
    spec_list = [package, spec.ref]
    if comment:
        spec_list.append(comment)
    return " ".join(spec_list)


def get_spec(line):
    # Rebuild old_spec
    (package, ref) = line.split(" ")
    ref_path = None

    if "/" in package:
        parts = package.split("/")
        package = parts[0]
        ref_path = "/".join(parts[1:])
    return PackageSpec(package, ref, ref_path)
