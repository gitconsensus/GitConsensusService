from github3apps import GithubApp, GithubAppInstall
from gitconsensus.repository import Repository
from gitconsensusservice import app


class GithubConsensusApp(GithubApp):
    def get_installation(self, installation_id):
        return GithubConsensusAppInstall(self, installation_id)


class GithubConsensusAppInstall(GithubAppInstall):
    def get_repository(self, username, repository_name):
        client = self.get_github3_client()
        return Repository(username, repository_name, client)


gh = GithubConsensusApp(app.config['GITHUB_APP_ID'], app.config['GITHUB_PRIVATE_KEY'])
