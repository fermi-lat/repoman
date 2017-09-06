import json
import logging
import os
from .error import RepomanError

logger = logging.getLogger(__name__)

RELEASE_COMMIT_PREFIX = "[repoman-release]"
RELEASE_COMMIT_MESSAGE = "Prepare release"
RELEASE_FILE = "repoman.release.json"
TARGET_DIR = "target"


def resolve_next_version(package, major=None, minor=None, patch=None):
    current_version = package.describe_version()
    split_version = current_version.split("-")
    (next_major, next_minor, next_patch) = [int(i) for i in split_version[:3]]
    pre_release = "-".join(split_version)[3:] if len(split_version) > 3 else ""
    len_args = sum([1 for i in [major, minor, patch] if i])

    if not pre_release and not len_args:
        raise RepomanError("Invalid version specification")

    if major:
        next_major += 1
        next_minor = 0
        next_patch = 0
    elif minor:
        next_minor += 1
        next_patch = 0
    elif patch:
        next_patch += 1

    version = "{:02}-{:02}-{:02}".format(next_major, next_minor, next_patch)
    return version


def prepare(package, release_version, tag_message, commit_message=None,
            tag_dependencies=True, remote="origin"):
    """
    Prepare for a release in git.

    Steps through several phases to ensure the repo is in a sane state
    and the manifest (packageList.txt) is ready to be released,
    resolving files accordingly. After this is done, a release file is
    written and changes are staged for the next step in the release
    process, ``perform``.

    :param package:
    :param release_version: Verion for the package to be released
    :param tag_message: Message for the annotated tag
    :param commit_message: Git Commit message to use after resolving
    the manifest and any other assets. If None, this defaults to
    ``{RELEASE_COMMIT_PREFIX} {RELEASE_COMMIT_MESSAGE} {tag}``, e.g.
    ``[repoman-release] Prepare release astro-01-01-01```
    :param tag_dependencies: If True, tag the dependencies with the
    tag as well.
    :param remote: Remote handle of where to push changes. Defaults
    to ``origin``.
    """
    # Assert everything is committed.
    if package.repo.is_dirty():
        raise RepomanError("Current working copy is dirty. Check git status.")

    current_ref = package.repo.head.commit.hexsha
    new_tag = _get_tag(package, release_version)
    do_resolve_release(package, new_tag, release_version, tag_message)

    full_commit_message = _get_commit_message(commit_message, new_tag)

    release_properties = dict(
        package=package.name,
        tag=new_tag,
        release_version=release_version,
        tag_message=tag_message,
        commit_message=full_commit_message,
        tag_dependencies=tag_dependencies,
        remote=remote,
        current_ref=current_ref
    )

    target_path = os.path.join(package.path, TARGET_DIR)
    release_file_path = os.path.join(target_path, RELEASE_FILE)
    if not os.path.exists(target_path):
        os.mkdir(target_path)
    with open(release_file_path, "w") as release_file:
        output = json.dumps(release_properties)
        release_file.write(output)


def perform(package, push=True):
    """
    Verify state from perform, commit changes, tag package(s),
    and push the tags
    :param package:
    :param push: If True, tagged packages will be pushed.
    """

    target_path = os.path.join(package.path, TARGET_DIR)
    release_file_path = os.path.join(target_path, RELEASE_FILE)

    if not os.path.exists(release_file_path):
        raise RepomanError("No release is currently prepared")

    with open(release_file_path, "r") as release_file:
        release_input = release_file.read()
        release_properties = json.loads(release_input)

    full_commit_message = release_properties["full_commit_message"]
    package.repo.commit(full_commit_message)

    tag = release_properties["tag"]
    tag_message = release_properties["tag_message"]
    remote = release_properties["remote"]
    tag_dependencies = release_properties["tag_dependencies"]

    packages = None
    package.repo.create_tag(tag, ref="HEAD", message=tag_message)

    if package.has_dependencies() and tag_dependencies:
        packages = package.read_manifest()
        # assert_packages_remote(packages)
        seen_dependencies = set()
        for dependency in packages:
            if dependency.name in seen_dependencies:
                logger.warning("Already tagged dependency: {}. "
                               "Skipping...".format(dependency.name))
            ref = dependency.ref
            dependency.repo.create_tag(tag, ref=ref, message=tag_message)
            seen_dependencies.add(dependency.name)

    if push:
        package.repo.remotes[remote].push(tag)
        if packages:
            for dependency in packages:
                dependency.repo.remotes[remote].push(tag)


def do_resolve_release(package, tag, version, tag_message):
    """
    Update the manifest and any other files that might need to be
    updated as part of a release, like release notes,
    documentation, or other.
    :param package:
    :param tag:
    :param version:
    """
    # FIXME: Write this
    # update_manifest(package, tag)
    # release_notes(package, tag, tag_message)
    pass


def _get_tag(package, version):
    return "-".join([package.name, version])


def _get_commit_message(commit_message, tag):
    prefix = RELEASE_COMMIT_PREFIX
    commit_message = commit_message or RELEASE_COMMIT_MESSAGE
    return " ".join([prefix, commit_message, tag])
