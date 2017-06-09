import click
import os
import sys
from .error import RepomanError
from .workspace import Workspace
from .package import read_package_list, read_package_list_file

PACKAGE_LIST = "packageList.txt"


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
    """Repoman is a repo and package management tool for
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
@click.option('--latest', is_flag=True,
              help="Ignore versions in package list and check out master")
@pass_ctx
def checkout(ctx, package, ref, force, latest):
    """Stage a Fermi package.
    REF may be Tag, Branch, or Commit. For more information,
    see help for git-checkout"""
    workspace = Workspace(ctx.workspace_dir, ctx.remote_base)
    workspace.checkout(package, ref, force=force)
    package_dir = os.path.join(ctx.workspace_dir, package)
    # Check if this is there is a package list
    if PACKAGE_LIST in os.listdir(package_dir):
        package_list_p = os.path.join(package_dir, PACKAGE_LIST)
        package_specs = read_package_list(package_list_p)
        if latest:
            package_specs = [[package] for (package, ref) in package_specs]
        try:
            workspace.checkout_packages(package_specs)
        except RepomanError as err:
            _print_err(err)
            sys.exit(1)



@cli.command("checkout-list")
@click.argument('package-list', type=click.File("r"))
@click.option('--force', is_flag=True,
              help="Force git checkout. This will throw away local changes")
@click.option('--latest', is_flag=True,
              help="Ignore versions in package list and check out master")
@pass_ctx
def checkout_list(ctx, package_list, force, latest):
    """Stage packages from a package list."""
    workspace = Workspace(ctx.workspace_dir, ctx.remote_base)
    package_specs = read_package_list_file(package_list)
    if latest:
        package_specs = [[package] for (package, ref) in package_specs]
    try:
        workspace.checkout_packages(package_specs, force=force)
    except RepomanError as err:
        _print_err(err)
        sys.exit(1)


def _print_err(err):
    for arg in err.args:
        click.echo(arg)


if __name__ == '__main__':
    cli()
