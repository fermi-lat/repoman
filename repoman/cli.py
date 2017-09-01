import click
import os
import sys
from .error import RepomanError
from .workspace import Workspace
from .package import Package, PackageSpec
from .manifest import find_manifest, read_manifest, read_manifest_file
from .release import resolve_next_version, prepare, perform


class RepomanCtx(object):

    def __init__(self, workspace_dir, remote_base):
        self.workspace_dir = workspace_dir
        self.remote_base = remote_base
        self.config = {}
        self.verbose = False

    def set_config(self, key, value):
        self.config[key] = value
        if self.verbose:
            click.echo('  config[%s] = %s' % (key, value), file=sys.stderr)

    def __repr__(self):
        return '<RepomanCtx %r>' % self.workspace_dir


pass_ctx = click.make_pass_decorator(RepomanCtx)


@click.group()
@click.option('--workspace', envvar='WORKSPACE_DIR', default=os.getcwd(),
              type=click.Path(),
              metavar='PATH', help='Changes the workspace.')
@click.option('--remote-base', envvar='REMOTE_BASE',
              default="git@github.com:fermi-lat",
              help='Github user/organization for repos')
@click.option('--config', nargs=2, multiple=True,
              metavar='KEY VALUE', help='Overrides a config key/value pair.')
@click.version_option('1.0')
@click.pass_context
def cli(ctx, workspace, remote_base, config):
    """Repoman is a repo and name management tool for
    Fermi's Software configuration.
    """
    # Create a repo object and remember it as as the context object.  From
    # this point onwards other commands can refer to it by using the
    # @pass_repo decorator.
    ctx.obj = RepomanCtx(os.path.abspath(workspace), remote_base)
    for key, value in config:
        ctx.obj.set_config(key, value)


@cli.command()
@click.argument('package')
@click.argument('ref', required=False)
@click.option('--force', is_flag=True,
              help="Force git checkout. This will throw away local changes")
@click.option('--master', is_flag=True,
              help="Ignore versions in name list and check out master")
@pass_ctx
def checkout(ctx, package, ref, force, master):
    """Stage a Fermi package.
    REF may be Tag, Branch, or Commit. For more information,
    see help for git-checkout"""
    workspace = Workspace(ctx.workspace_dir, ctx.remote_base)
    workspace.checkout(package, ref, force=force)
    package_dir = os.path.join(ctx.workspace_dir, package)
    # Check if this is there is a name list
    manifest_path = find_manifest(package_dir)
    if manifest_path is not None:
        package_specs = read_manifest(manifest_path)
        if master:
            package_specs = [PackageSpec(package) for
                             (package, ref, ref_path) in package_specs]
        try:
            workspace.checkout_packages(package_specs)
        except RepomanError as err:
            _print_err(err)
            sys.exit(1)


@cli.command("checkout-list")
@click.argument('package-list', type=click.File("r"))
@click.option('--force', is_flag=True,
              help="Force git checkout. This will throw away local changes")
@click.option('--master', is_flag=True,
              help="Ignore versions in name list and check out master")
@pass_ctx
def checkout_list(ctx, package_list, force, master):
    """Stage packages from a package list."""
    workspace = Workspace(ctx.workspace_dir, ctx.remote_base)
    package_specs = read_manifest_file(package_list)
    if master:
        package_specs = [[package] for (package, ref) in package_specs]
    try:
        workspace.checkout_packages(package_specs, force=force)
    except RepomanError as err:
        _print_err(err)
        sys.exit(1)


@cli.command("release")
@click.argument('package')
@click.argument('release-message')
@click.option('--major', is_flag=True,
              help="Bump next major version")
@click.option('--minor', is_flag=True,
              help="Bump next minor version")
@click.option('--patch', is_flag=True,
              help="Bump next patch version")
@pass_ctx
def release(ctx, package, release_message, major, minor, patch):
    """Prepare and perform a release.

    This command executes both the prepare and perform steps
    of a release process.
    """
    package = _get_package(ctx, package)
    version = resolve_next_version(package, major, minor, patch)
    # FIXME:
    # prepare(package, version, release_message)
    # perform(package, version)


@cli.command("release-prepare")
@click.argument('package')
@click.argument('release-message')
@click.option('--major', is_flag=True,
              help="Bump next major version")
@click.option('--minor', is_flag=True,
              help="Bump next minor version")
@click.option('--patch', is_flag=True,
              help="Bump next patch version")
@pass_ctx
def release_prepare(ctx, package, release_message, major, minor, patch):
    """Prepare for a release in git.

    Steps through several phases to ensure the manifest is ready to be
    released and then prepares local git with a tagged version of the
    release and a record in the local copy of the parameters used.
    """
    package = _get_package(ctx, package)
    version = resolve_next_version(package, major, minor, patch)
    # FIXME: prepare(package, version, release_message)


@cli.command("release-perform")
@click.argument('package')
@pass_ctx
def release_perform(ctx, package):
    """Perform a release only.

    Verify tags and remotes are in order and push them to the
    appropriate remotes."""
    package = _get_package(ctx, package)
    version = package.describe_version()
    # FIXME: perform(package, version)


def _get_package(ctx, name):
    workspace = Workspace(ctx.workspace_dir, ctx.remote_base)
    package_dir = os.path.join(ctx.workspace_dir, name)
    package = Package(name, workspace, package_dir)


def _print_err(err):
    for arg in err.args:
        click.echo(arg)


if __name__ == '__main__':
    cli()
