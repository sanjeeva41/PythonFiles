from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from github import Github
import json

from time import sleep
from nipyapi import canvas, config
from config import LONG_SLEEP, NIFI_XQUERY_PROCESSOR_GROUP_UUID, OWL_FILE_PATH
from config import ENDPOINT, GITHUB_TOKEN, GITHUB_OWNER, REPO_NAME, HOST, OWL_FILE_NAME

@view_defaults(
    route_name=ENDPOINT, renderer="json", request_method="POST"
)
class PayloadView(object):
    """
    View receiving of Github payload. By default, this view it's fired only if
    the request is json and method POST.
    """

    def __init__(self, request):
        self.request = request
        # Payload from Github, it's a dict
        self.payload = self.request.json
        
    def executeNifiProcessor(self):
        canvas.schedule_process_group(NIFI_XQUERY_PROCESSOR_GROUP_UUID, True)
        sleep(LONG_SLEEP)
        canvas.schedule_process_group(NIFI_XQUERY_PROCESSOR_GROUP_UUID, False)
        
    def downloadFile(self):
    
        git = Github(GITHUB_TOKEN)

        user = git.get_user()
        repo = user.get_repo(REPO_NAME)
        
        contents = repo.get_contents(OWL_FILE_NAME)
        data = contents.decoded_content.decode("utf-8")
            
        f = open(OWL_FILE_PATH, "w")
        f.write(data)
        f.close()
        
        self.executeNifiProcessor()
        
        print("OWL File is uploaded successfully!")

    @view_config(header="X-Github-Event:push")
    def payload_push(self):
    
        """This method is a continuation of PayloadView process, triggered if
        header HTTP-X-Github-Event type is Push"""
        
        print("No. commits in push:", len(self.payload['commits']))
        self.downloadFile()
        return Response("success")

def create_webhook():
    """ Creates a webhook for the specified repository.

    This is a programmatic approach to creating webhooks with PyGithub's API. If you wish, this can be done
    manually at your repository's page on Github in the "Settings" section. There is a option there to work with
    and configure Webhooks.
    """
    
    EVENTS = ["push", "pull_request"]
    
    config = {
        "url": "http://{host}/{endpoint}".format(host=HOST, endpoint=ENDPOINT),
        "content_type": "json"
    }

    g = Github(GITHUB_TOKEN)
    repo = g.get_repo("{owner}/{repo_name}".format(owner=GITHUB_OWNER, repo_name=REPO_NAME))
    repo.create_hook("web", config, EVENTS, active=True)


if __name__ == "__main__":
    config = Configurator()

    # create_webhook()

    config.add_route(ENDPOINT, "/{}".format(ENDPOINT))
    config.scan()

    app = config.make_wsgi_app()
    server = make_server("0.0.0.0", 80, app)
    server.serve_forever()
    
# References:
# ===============
# https://pygithub.readthedocs.io/en/latest/examples/Webhook.html#creating-and-listening-to-webhooks-with-pygithub-and-pyramid
