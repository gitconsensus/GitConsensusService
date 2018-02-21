import click
import re
from gitconsensusservice.services import github
import yaml
from gitconsensus.repository import Repository


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


@cli.command(short_help="Get an authentication token for the provided installation.")
@click.argument('install_id')
def install_repos(install_id):
    token = github.get_installation_repositories(install_id)
    dump(token)


@cli.command(short_help="List details about the current application.")
def application():
    dump(github.get_app())


@cli.command(short_help="Get JWT Authentication Token for this application.")
def jwt():
    click.echo(github.get_jwt())


@cli.command(short_help="List all open pull requests for the specific install and repository.")
@click.argument('install_id')
@click.argument('username')
@click.argument('repository_name')
def prs(install_id, username, repository_name):
    dump(github.list_prs(install_id, username, repository_name))


@cli.command(short_help="Display detailed information about a specific pull request")
@click.argument('install_id')
@click.argument('username')
@click.argument('repository_name')
@click.argument('pull_request')
def pr(install_id, username, repository_name, pull_request):
    repo = get_repository(install_id, username, repository_name)
    request = repo.getPullRequest(pull_request)
    click.echo("PR#%s: %s" % (request.number, request.pr.title))
    consensus = repo.getConsensus()
    click.echo("Mergeable:    %s" % (consensus.isMergeable(request),))
    click.echo("Is Blocked:   %s" % (request.isBlocked(),))
    click.echo("Is Allowed:   %s" % (consensus.isAllowed(request),))
    click.echo("Has Quorum:   %s" % (consensus.hasQuorum(request),))
    click.echo("Has Votes:    %s" % (consensus.hasVotes(request),))
    click.echo("Has Aged:     %s" % (consensus.hasAged(request),))
    click.echo("Should Close: %s" % (request.shouldClose(),))
    click.echo("Last Update:  %s" % (request.hoursSinceLastUpdate(),))


def get_repository(install_id, username, repository_name):
    client = github.get_github3_client(install_id)
    return Repository(username, repository_name, client)


def dump(obj):
    click.echo(yaml.dump(obj, default_flow_style=False))


if __name__ == '__main__':
    cli()
