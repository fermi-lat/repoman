from git import Repo
from git.exc import GitCommandError
from .error import WorkspaceError
import os
import shutil

DEFAULT_REMOTE_BASE = "git@github.com:fermi-lat"

"""
The Workspace Module is used for staging packages from repositories
to a working directory.
"""


class Workspace:

    def __init__(self, working_path, remote_base=None):
        self.working_path = working_path
        self.remote_base = remote_base or DEFAULT_REMOTE_BASE

    def checkout(self, package, ref=None, force=False, clobber=False):
        """
        Checkout a package repo by name.
        :param package: Name of the package you are checking out
        :param ref: Tag, Branch, or Commit. See `man git-checkout`
        :param force: Force git checkout. This throws away local
        changes in the package.
        :param clobber: Remove the directory named `package` first
        """
        repo_path = os.path.join(self.working_path, package)
        # This assumes you aren't using windows

        if clobber:
            if os.path.isdir(repo_path):
                shutil.rmtree(repo_path)

        if os.path.exists(repo_path):
            git_repo = Repo(repo_path)
            if git_repo.working_tree_dir != repo_path:
                raise ValueError("Not in working tree")
        else:
            git_repo = Repo.init(repo_path)
            # Not clear it this does anything, but can't hurt.
            with git_repo.config_writer() as config:
                config.set_value("core", "sparsecheckout", "true")

        repo_url = os.path.join(self.remote_base, package) + ".git"
        if not git_repo.remotes:
            git_repo.create_remote("origin", repo_url)
        origin = git_repo.remotes["origin"]

        # Not sure if this needs to be optimized
        try:
            origin.fetch(tags=True)
            origin.fetch()  # This is required for RHEL6/git1.8 support
        except GitCommandError as e:
            raise WorkspaceError("Unable to fetch tags for %s. Please verify "
                                 "package exists and you are accessing it "
                                 "properly. You may also need to wait a few "
                                 "minutes" % package,
                                 "Repo: " + repo_url,
                                 e.stderr)

        checkout_ref = ref or git_repo.head.ref
        checkout_args = ["-f"] if force else []
        checkout_args.append(checkout_ref)
        try:
            git_repo.git.checkout(*checkout_args)
        except GitCommandError as e:
            raise WorkspaceError("Unable to checkout package: %s, " 
                                 "You may need to force checkout. \n"
                                 "Command Output: " % package,
                                 e.stderr)

    def checkout_packages(self, package_specs, force=False, clobber=False):
        """
        Checkout a bunch of packages
        :param package_specs: list of (package, ref) pairs
        :param force: Force git checkout. This throws away local
        changes in the packages.
        :param clobber: Clobber the package directories
        """
        for package_spec in package_specs:
            package = package_spec[0]
            ref = package_spec[1] if len(package_spec) > 1 else None
            self.checkout(package, ref, force=force, clobber=clobber)
