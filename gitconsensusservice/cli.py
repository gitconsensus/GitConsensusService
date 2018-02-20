import click
import re
from gitconsensusservice.services import github
import yaml


@click.group()
@click.pass_context
def cli(ctx):
    if ctx.parent:
        print(ctx.parent.get_help())


@cli.command(short_help="List installation IDs available to this application.")
def installs():
    installs = github.get_installations()
    for install in installs:
        click.echo(install)


@cli.command(short_help="List details about a specific installation.")
@click.argument('install_id')
def install(install_id):
    dump(github.get_installation(install_id))


@cli.command(short_help="Get an authentication token for the provided installation.")
@click.argument('install_id')
def install_token(install_id):
    token = github.get_installation_token(install_id)
    click.echo(token)


@cli.command(short_help="List details about the current application.")
def application():
    dump(github.get_app())


@cli.command(short_help="Get JWT Authentication Token for this application.")
def jwt():
    click.echo(github.get_jwt())


def dump(obj):
    click.echo(yaml.dump(obj, default_flow_style=False))


if __name__ == '__main__':
    cli()
