
RELEASE_COMMIT_PREFIX = "[repoman-release]"
RELEASE_COMMIT_MESSAGE = "Prepare release"


def resolve_next_version(package, major=None, minor=None, patch=None):
    current_version = package.describe_version()
    split_version = current_version.split("-")
    (next_major, next_minor, next_patch) = [int(i) for i in split_version[:3]]
    cur_more = "-".join(split_version)[3:] if len(split_version) > 3 else ""
    len_args = sum([1 for i in [major, minor, patch] if i])

    if not cur_more and not len_args:
        raise ValueError("Invalid version specification")

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


def prepare(package, release_version, tag_message, commit_message=None):
    """
    Prepare for a release in git.

    Steps through several phases to ensure the manifest is ready to be
    released and then prepares local git with a tagged version of the
    release and a record in the local copy of the parameters used.

    :param package:
    :param release_version: Verion for the package to be released
    :param tag_message: Message for the annotated tag
    :param commit_message: Git Commit message to use after resolving
    the manifest and any other assets. If None, this defaults to
    ``{RELEASE_COMMIT_PREFIX} {RELEASE_COMMIT_MESSAGE} {tag}``, e.g.
    ``[repoman-release] Prepare release astro-01-01-01```
    """

    assert_committed(package)
    tag = _get_tag(package, release_version)
    do_resolve_release(package, release_version)

    full_commit_message = _get_commit_message(commit_message, tag)
    # FIXME: package.repo.commit(full_commit_message)

    # FIXME: package.repo.tag(ref="HEAD", tag=tag)
    if package.has_dependencies():
        packages = package.read_manifest()
        # assert_packages_remote(packages)
        for dependency in packages:
            tag_dependency(dependency, tag, tag_message)
    # TODO: Add support for next_version?


def perform(package, version, remote="origin"):
    """
    Verify tags and remotes are in order and push them to the
    appropriate remotes.
    :param package:
    :param version:
    :param remote:
    :return:
    """
    tag = _get_tag(package, version)
    # FIXME: assert_tagged(package, tag)
    packages = None
    if package.has_dependencies():
        packages = package.read_manifest()
    # FIXME: package.remotes[remote].push(tag)
    if packages:
        for dependency in packages:
            _push_dependency_tags(dependency, tag, remote=remote)


def assert_committed(package, check_workspace=False):
    """
    Verify the package has no uncommitted changes.
    :param package:
    :param check_workspace: If true, check if workspace has any
    uncomitted changes too.
    """
    # FIXME: Write this
    pass


def do_resolve_release(package, version):
    """
    Update the manifest and any other files that might need to be
    updated as part of a release, like release notes,
    documentation, or other.
    :param package:
    :param version:
    :return:
    """
    tag = _get_tag(package, version)
    # FIXME: Write this
    # update_manifest(package)
    # release_notes(package)
    pass


def tag_dependency(package, tag, tag_message):
    package.repo.tag(tag, ref=package.ref, message=tag_message)


def _push_dependency_tags(package, tag, remote=None, tag_message=None):
    package.remotes[remote].push(tag)


def _get_tag(package, version):
    return "-".join([package.name, version])


def _get_commit_message(commit_message, tag):
    prefix = RELEASE_COMMIT_PREFIX
    commit_message = commit_message or RELEASE_COMMIT_MESSAGE
    return " ".join([prefix, commit_message, tag])
