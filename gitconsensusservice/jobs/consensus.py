from gitconsensusservice import app, celery
from services.githubapp import gh


@celery.task
def process_installs(synchronous=False):
    print('Processing all installations')
    installs = gh.get_installations()
    for install in installs:
        if synchronous:
            process_installation(install, True)
        else:
            process_installation.delay(install)


@celery.task
def process_installation(installation_id, synchronous=False):
    print('Processing installation %s' % (installation_id))
    installation = gh.get_installation(installation_id)
    repositories = installation.get_repositories()
    for repository in repositories:
        user, repo = repository.split('/')
        process_repository(installation_id, user, repo, True)


@celery.task
def process_repository(installation_id, user, repo, synchronous=False):
    print('Processing %s/%s as installation %s' % (user, repo, installation_id))
    installation = gh.get_installation(installation_id)
    repository = installation.get_repository(user, repo)

    # has consensus rules?
    if not repository.rules:
        print('%s/%s does not have any consensus rules.' % (user, repo))
        return

    prs = installation.get_pr_numbers(user, repo)
    for pr in prs:
        if synchronous:
            process_pull_request(installation_id, user, repo, pr)
        else:
            process_pull_request.delay(installation_id, user, repo, pr)


@celery.task
def process_pull_request(installation_id, user, repo, pull_request):
    print('Processing %s/%s #%s as installation %s' % (user, repo, pull_request, installation_id))
    installation = gh.get_installation(installation_id)
    repository = installation.get_repository(user, repo)
    request = repository.getPullRequest(pull_request)
    if request.validate():
        print("Merging PR#%s" % (request.number,))
        request.vote_merge()
    elif request.shouldClose():
        print("Closing PR#%s" % (request.number,))
        request.close()
    else:
        request.addInfoLabels()
