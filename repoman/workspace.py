import git
from git import Repo
from git.exc import GitCommandError
from .error import WorkspaceError
import os
import shutil
import logging
from collections import OrderedDict
import time

logger = logging.getLogger(__name__)

DEFAULT_REMOTE_BASE = "git@github.com:fermi-lat"

"""
The Workspace Module is used for staging packages from repositories
to a working directory.
"""


SLEEP_INTERVALS = [0.5, 2.5, 5]


class Workspace:

    def __init__(self, working_path, remote_base=None):
        self.working_path = working_path
        self.remote_base = remote_base or DEFAULT_REMOTE_BASE
        self.repo = None
        self.bom = OrderedDict()
        self.git_version = _git_version()
        self.fetched = []

    def checkout(self, package, ref=None, ref_path=None, refs=None,
                 force=False, clobber=False, in_place=False):
        """
        Checkout a name repo by name.
        :param package: Name of the name you are checking out
        :param ref: Tag, Branch, or Commit. See `man git-checkout`
        :param ref_path: Specific path to checkout
        :param refs: List of Tags, Branches, or Commits, in decreasing
        priority, to check out. Master is implicit at the end.
        :param force: Force git checkout. This throws away local
        changes in the name. This also implies forcing to checkout
        what's in origin.
        :param clobber: Remove the directory named `name` first
        :param in_place: If True, use the working_path as the repo path
        """
        repo_path = self.working_path
        if not in_place:
            repo_path = os.path.join(self.working_path, package)
        # This assumes you aren't using windows

        if clobber and not in_place:
            if os.path.isdir(repo_path):
                shutil.rmtree(repo_path)

        repo = self.get_or_init_repo(repo_path)
        repo_url = os.path.join(self.remote_base, package) + ".git"
        if not repo.remotes:
            repo.create_remote("origin", repo_url)

        # Check if package has already been fetched.
        # This happens if we are checking out a path at a different ref
        if package not in self.fetched:
            self._fetch(package, repo, repo_url)

        checkout_ref = ref or repo.head.ref

        # If a ref is listed in the list, use that instead
        if refs:
            repo_refs = repo.references
            origin_refs = repo.remotes.origin.refs
            for ref in refs:
                if _has_commit(repo, ref):
                    checkout_ref = ref
                    break

                # Prefer origin refs
                if ref in origin_refs:
                    checkout_ref = origin_refs[ref]
                    break

                # fall back to local refs if not at origin
                if ref in repo_refs:
                    checkout_ref = repo_refs[ref]
                    break

        spec_str = "{} {}".format(package, checkout_ref or "")
        if ref_path:
            spec_str += " for path {}".format(ref_path)
        logging.info("Checkout out spec: {}".format(spec_str))

        checkout_args = ["-f"] if force else []
        checkout_args.append(checkout_ref)
        if ref_path:
            checkout_args.append(ref_path)
        try:
            repo.git.checkout(*checkout_args)
            if force:
                repo.git.reset("--hard", checkout_ref)
            self.bom[package] = dict(commit=repo.head.commit.hexsha)
            if checkout_ref in repo.tags:
                self.bom[package]["tag"] = checkout_ref
            if not repo.head.is_detached:
                self.bom[package]["branch"] = repo.head.ref.name
        except GitCommandError as e:
            raise WorkspaceError("Unable to checkout name: %s, "
                                 "You may need to force checkout. \n"
                                 "Command Output: " % package,
                                 e.stderr)

    def get_or_init_repo(self, repo_path):
        git_dir = os.path.join(repo_path, ".git")

        if os.path.exists(git_dir):
            git_repo = Repo(repo_path)
            if git_repo.working_tree_dir != repo_path:
                raise ValueError("Not in working tree")
        else:
            git_repo = Repo.init(repo_path)
            # Not clear it this does anything, but can't hurt.
            with git_repo.config_writer() as config:
                config.set_value("core", "sparsecheckout", "true")
        return git_repo

    def checkout_packages(self, package_specs, refs=None, force=False,
                          clobber=False):
        """
        Checkout a bunch of packages
        :param package_specs: list of (name, ref) pairs
        :param refs: Prioritized list of refs to checkout, with leftmost
        priority).
        :param force: Force git checkout. This throws away local
        changes in the packages.
        :param clobber: Clobber the name directories
        """
        for spec in package_specs:
            self.checkout(spec.name, spec.ref, spec.ref_path,
                          refs=refs, force=force, clobber=clobber)

    def _fetch(self, package, repo, repo_url):
        remote = repo.remotes["origin"]
        git_major, git_minor = self.git_version
        retry = 0
        # Not sure if this needs to be optimized
        while True:
            try:
                remote.fetch(tags=True)
                if git_major == 1 and git_minor < 9:
                    logger.debug("You are using an older version of git.")
                    remote.fetch()  # This is required for RHEL6/git1.8 support
                self.fetched.append(package)
                break
            except GitCommandError as e:
                if retry < len(SLEEP_INTERVALS):
                    logger.debug("Error checkout out {}, retrying in {}s"
                                 .format(package, SLEEP_INTERVALS[retry]))
                    time.sleep(SLEEP_INTERVALS[retry])
                    retry += 1
                    continue
                raise WorkspaceError("Unable to fetch tags for %s. Please verify "
                                     "name exists and you are accessing it "
                                     "properly. You may also need to wait a few "
                                     "minutes" % package,
                                     "Repo: " + repo_url,
                                     e.stderr)


def _git_version():
    git_version_str = git.cmd.Git().version().split()[2]
    git_version_spec = git_version_str.split(".")
    git_major, git_minor = git_version_spec[0:2]
    return int(git_major), int(git_minor)


def _has_commit(repo, ref):
    try:
        repo.git.show("--oneline", ref)
        return True
    except GitCommandError as e:
        return False
