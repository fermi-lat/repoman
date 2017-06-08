import click
import os
import sys
from .workspace import Workspace
from .package import read_package_list

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


@cli.command("stage-package")
@click.argument('package')
@click.argument('ref', required=False)
@pass_ctx
def stage_package(ctx, package, ref):
    """Stage a Fermi package.
    REF may be Tag, Branch, or Commit. For more information,
    see help for git-checkout"""
    workspace = Workspace(ctx.workspace_dir, ctx.remote_base)
    workspace.checkout(package, ref)
    package_dir = os.path.join(ctx.workspace_dir, package)
    if PACKAGE_LIST in os.listdir(package_dir):
        package_list = os.path.join(package_dir, PACKAGE_LIST)
        package_specs = read_package_list(package_list)
        workspace.checkout_packages(package_specs)

if __name__ == '__main__':
    cli()
