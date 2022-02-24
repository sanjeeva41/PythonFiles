
from pyramid.config import Configurator
from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from github import Github
import json

from time import sleep
from nipyapi import canvas, config
from config import LONG_SLEEP, NIFI_XQUERY_PROCESSOR_GROUP_UUID, OWL_FILE_PATH, SHORT_SLEEP
from config import ENDPOINT, GITHUB_TOKEN, GITHUB_OWNER, REPO_NAME, HOST, OWL_FILE_NAME

def executeNifiProcessor():
    canvas.schedule_process_group(NIFI_XQUERY_PROCESSOR_GROUP_UUID, True)
    sleep(LONG_SLEEP)
    canvas.schedule_process_group(NIFI_XQUERY_PROCESSOR_GROUP_UUID, False)
    
def downloadFile():

    print("Downloading the OWL file from Github")

    git = Github(GITHUB_TOKEN)

    user = git.get_user()
    repo = user.get_repo(REPO_NAME)
    
    contents = repo.get_contents(OWL_FILE_NAME)
    data = contents.decoded_content.decode("utf-8")
        
    f = open(OWL_FILE_PATH, "w")
    f.write(data)
    f.close()
    
    sleep(SHORT_SLEEP)
    
    print("OWL File downloaded successfully")
    
    sleep(LONG_SLEEP)
    
    print("Started NiFi Processors execution:")
    
    executeNifiProcessor()
    
    print("Completed the NiFi processors execution")


if __name__ == "__main__":

    downloadFile()
    
    
# References:
# ===============
# https://pygithub.readthedocs.io/en/latest/examples/Webhook.html#creating-and-listening-to-webhooks-with-pygithub-and-pyramid
