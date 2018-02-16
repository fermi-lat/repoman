import json
import logging
import os
import re
from .error import RepomanError

logger = logging.getLogger(__name__)

RELEASE_COMMIT_PREFIX = "[repoman-release]"
RELEASE_COMMIT_MESSAGE = "Prepare release"
RELEASE_FILE = "repoman_release.json"
TARGET_DIR = "target"


def resolve_next_version(package, major=None, minor=None, patch=None):
    current_version = package.describe()
    if not current_version:
        raise RepomanError("No valid tag found")
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


def prepare(package, release_version, release_message, commit_message=None,
            remote="origin"):
    """
    Prepare for a release in git.

    Steps through several phases to ensure the repo is in a sane state
    and the manifest (packageList.txt) is ready to be released,
    resolving files accordingly. After this is done, a release file is
    written and changes are staged for the next step in the release
    process, ``perform``.

    :param package:
    :param release_version: Verion for the package to be released
    :param release_message: Message for the annotated tag. If
    available,
    :param commit_message: Git Commit message to use after resolving
    the manifest and any other assets. If None, this defaults to
    ``{RELEASE_COMMIT_PREFIX} {RELEASE_COMMIT_MESSAGE} {tag}``, e.g.
    ``[repoman-release] Prepare release astro-01-01-01```
    :param remote: Remote handle of where to push changes. Defaults
    to ``origin``.
    """
    # Assert everything is committed.
    if package.repo.is_dirty():
        raise RepomanError("Current working copy is dirty. Check git status.")

    current_ref = package.repo.head.commit.hexsha
    new_tag = _get_tag(package, release_version)

    full_commit_message = _get_commit_message(commit_message, new_tag)

    release_properties = dict(
        package=package.name,
        tag=new_tag,
        release_version=release_version,
        release_message=release_message,
        commit_message=full_commit_message,
        remote=remote,
        current_ref=current_ref
    )

    target_path = os.path.join(package.path, TARGET_DIR)
    release_file_path = os.path.join(target_path, RELEASE_FILE)
    do_resolve_release(package, release_properties)
    if not os.path.exists(target_path):
        os.mkdir(target_path)
    with open(release_file_path, "w") as release_file:
        output = json.dumps(release_properties)
        release_file.write(output)


def perform(package, push=True):
    """
    Verify state from perform, commit changes, tag package(s),
    and push the tags
    :param package: Package to release
    :param push: If True, the tag will be pushed.
    """

    target_path = os.path.join(package.path, TARGET_DIR)
    release_file_path = os.path.join(target_path, RELEASE_FILE)

    if not os.path.exists(release_file_path):
        raise RepomanError("No release is currently prepared")

    with open(release_file_path, "r") as release_file:
        release_input = release_file.read()
        release_properties = json.loads(release_input)

    tag = release_properties["tag"]
    # Verify tag doesn't exist
    if tag in package.repo.tags:
        raise RepomanError("Tag {} already exists".format(tag))

    commit_message = release_properties["commit_message"]
    # Get a list of changed files and add them to the index for commmit
    for item in package.repo.index.diff(None):
        package.repo.index.add([item.a_path])
    # Perform commit with message
    package.repo.index.commit(commit_message)

    tag = release_properties["tag"]
    release_message = release_properties["release_message"]
    remote = release_properties["remote"]
    package.repo.create_tag(tag, ref="HEAD", message=release_message,
                            cleanup="whitespace")

    if push:
        package.repo.remotes[remote].push(tag)


def do_resolve_release(package, release_properties):
    """
    Update the manifest and any other files that might need to be
    updated as part of a release, like release notes,
    documentation, or other.
    :param package: The package to be released
    :param release_properties: A dict structure of release information
    """
    changelog_path = os.path.join(package.path, "CHANGELOG.md")
    if os.path.exists(changelog_path):
        new_lines = _new_changelog_lines(
            changelog_path,  release_properties.get("release_message")
        )
        with open(changelog_path, "w") as changelog_file:
            changelog_file.writelines(new_lines)


def _get_tag(package, version):
    return "-".join([package.name, version])


def _get_commit_message(commit_message, tag):
    prefix = RELEASE_COMMIT_PREFIX
    commit_message = commit_message or RELEASE_COMMIT_MESSAGE
    return " ".join([prefix, commit_message, tag])


def _new_changelog_lines(changelog_file, release_message):
    release_message = release_message or ""
    release_message = release_message.strip()
    release_message_lines = release_message.splitlines(True)
    lines = []
    with open(changelog_file) as changelog_file:
        for line in changelog_file:
            if release_message and re.match(r"^## \[", line):
                lines.extend(release_message_lines)
                lines.append("\n\n")
            lines.append(line)
    return lines
