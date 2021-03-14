from gitconsensusservice import app, celery
from gitconsensusservice.services.githubapp import gh


@celery.task
def process_installs(synchronous=False):
    print('Processing all installations')
    installs = gh.get_installations()
    for install in installs:
        if synchronous:
            try:
                process_installation(install, True)
            except Exception as error:
                print('Failed to process install %s due to error:' % install)
                print(error)
        else:
            process_installation.delay(install)


@celery.task
def process_installation(installation_id, synchronous=False):
    print('Processing installation %s' % (installation_id))
    installation = gh.get_installation(installation_id)
    repositories = installation.get_repositories()
    for repository in repositories:
        user, repo = repository.split('/')
        try:
            if synchronous:
                process_repository(installation_id, user, repo, True)
            else:
                process_repository.delay(installation_id, user, repo, False)
        except Exception as error:
            print('Failed to process %s/%s due to error:' % (user, repo))
            print(error)



@celery.task
def process_repository(installation_id, user, repo, synchronous=False):
    print('Processing %s/%s as installation %s' % (user, repo, installation_id))
    installation = gh.get_installation(installation_id)
    repository = installation.get_repository(user, repo)

    # has consensus rules?
    if not repository.rules:
        print('%s/%s does not have any consensus rules.' % (user, repo))
        return

    # Add labels
    if synchronous:
        process_repository_labels(installation_id, user, repo)
    else:
        process_repository_labels.delay(installation_id, user, repo)

    prs = installation.get_pr_numbers(user, repo)
    for pr in prs:
        if synchronous:
            process_pull_request(installation_id, user, repo, pr)
        else:
            process_pull_request.delay(installation_id, user, repo, pr)


color_notice = 'fbf904'
color_positive = '0052cc'
color_negative = 'ee0701'
label_colors = {
    'License Change': color_notice,
    'Consensus Change': color_notice,
    'Has Quorum': color_positive,
    'Needs Votes': color_negative,
    'Passing': color_positive,
    'Failing': color_negative,
    'gc-merged': color_positive,
    'gc-closed': color_negative,
}


@celery.task
def process_repository_labels(installation_id, user, repo):
    print('Checking %s/%s\'s labels as installation %s' % (user, repo, installation_id))
    installation = gh.get_installation(installation_id)
    repository = installation.get_repository(user, repo)
    labels = repository.get_labels()
    for label, color in label_colors.items():
        if label not in labels:
            print('Creating label %s with color #%s' % (label, color))
            repository.repository.create_label(label, color)
        elif color != labels[label].color:
            print('Reseting label %s to color #%s' % (label, color))
            labels[label].update(label, color)


@celery.task
def process_pull_request(installation_id, user, repo, pull_request):
    print('Processing %s/%s #%s as installation %s' % (user, repo, pull_request, installation_id))
    installation = gh.get_installation(installation_id)
    repository = installation.get_repository(user, repo)
    if not repository.rules:
        print('%s/%s does not have any consensus rules.' % (user, repo))
        return

    # It is possible that this will 404 here if an issue was passed in as a pull request.
    request = repository.getPullRequest(pull_request)
    if request.validate():
        print("Merging PR#%s" % (request.number,))
        request.vote_merge()
    elif request.shouldClose():
        print("Closing PR#%s" % (request.number,))
        request.close()
    else:
        request.addInfoLabels()


@celery.task
def remove_pull_request_labels(installation_id, user, repo, pull_request):
    print('Processing %s/%s #%s as installation %s' % (user, repo, pull_request, installation_id))
    installation = gh.get_installation(installation_id)
    repository = installation.get_repository(user, repo)
    request = repository.getPullRequest(pull_request)
    request.cleanInfoLabels()
