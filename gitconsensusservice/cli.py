import click
import yaml
from gitconsensusservice import app
from gitconsensusservice.services.githubapp import gh
from gitconsensusservice.jobs import consensus


@click.group()
@click.pass_context
def cli(ctx):
    if ctx.parent:
        print(ctx.parent.get_help())


@cli.command(short_help="List installation IDs available to this application.")
def installs():
    installs = gh.get_installations()
    for install in installs:
        click.echo(install)


@cli.command(short_help="List details about a specific installation.")
@click.argument('install_id')
def install(install_id):
    dump(get_githubapp_install(install_id).get_details())


@cli.command(short_help="Get an authentication token for the provided installation.")
@click.argument('install_id')
def install_token(install_id):
    dump(get_githubapp_install(install_id).get_auth_token())


@cli.command(short_help="List all repositories for an installation.")
@click.argument('install_id')
def install_repos(install_id):
    dump(get_githubapp_install(install_id).get_repositories())


@cli.command(short_help="List all available repositories with gitconsensus enabled.")
def list_repos():
    installs = gh.get_installations()
    for install_id in installs:
        click.echo('Install %s:' % install_id)
        installation = get_githubapp_install(install_id)
        repos = installation.get_repositories()
        for repo in repos:
            user, repo = repo.split('/')
            repository = installation.get_repository(user, repo)
            if repository.rules:
                click.echo('\t%s/%s' % (user, repo))


@cli.command(short_help="List details about the current application.")
def application():
    dump(gh.get_app())


@cli.command(short_help="List all labels for the specific install and repository.")
@click.argument('install_id')
@click.argument('username')
@click.argument('repository_name')
def labels(install_id, username, repository_name):
    gc_repo = get_repository(install_id, username, repository_name)
    labels = gc_repo.get_labels()
    dump(labels)



@cli.command(short_help="List all labels for the specific install and repository.")
@click.argument('install_id')
@click.argument('username')
@click.argument('repository_name')
def process_repository_labels(install_id, username, repository_name):
    consensus.process_repository_labels(install_id, username, repository_name)



@cli.command(short_help="Get JWT Authentication Token for this application.")
def jwt():
    click.echo(gh.get_jwt())


@cli.command(short_help="List all open PRs for the specific install and repository.")
@click.argument('install_id')
@click.argument('username')
@click.argument('repository_name')
def prs(install_id, username, repository_name):
    dump(get_githubapp_install(install_id).list_prs(username, repository_name))


@cli.command(short_help="Display detailed information about a specific pull request.")
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


@cli.command(short_help="Process pull requests for all installations.")
@click.argument('installation', required=False)
@click.option('--synchronous/--no-synchronous', default=True)
def process(synchronous, installation):
    if not installation:
        consensus.process_installs(synchronous)
    else:
        consensus.process_installation(installation, synchronous)


def get_githubapp_install(install_id):
    return gh.get_installation(install_id)


def get_repository(install_id, username, repository_name):
    return get_githubapp_install(install_id).get_repository(username, repository_name)


def dump(obj):
    click.echo(yaml.dump(obj, default_flow_style=False))


if __name__ == '__main__':
    cli()
