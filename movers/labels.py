import json
from libs import *

'''
INPUT:
    source_url: the root url for the GitHub API
    source: the team and repo '<team>/<repo>' to retrieve labels from
OUTPUT: retrieved labels if request was successful. False otherwise
'''
def download_labels(source_url, source, credentials):
    print "Downloading labels"
    url = source_url+"repos/"+source+"/labels?filter=all"
    r = get_req(url, credentials)
    status = check_res(r)
    if status:
        return json.loads(r.text)
    return False

'''
INPUT:
    labels: python list of dicts containing label info to be POSTED to GitHub
    destination_url: the root url for the GitHub API
    destination: the team and repo '<team>/<repo>' to post labels to
OUTCOME: Post labels to GitHub
OUTPUT: Null
'''
def create_labels(labels, destination_url, destination, credentials):
    print "Creating labels"
    url = destination_url+"repos/"+destination+"/labels?filter=all"
    #download labels from the destination and pass them into dictionary of label names
    check_labels = download_labels(destination_url, destination, credentials)
    existing_labels = {}
    for existing_label in check_labels:
        existing_labels[existing_label["name"]] = existing_label
    for label in labels:
        #for every label that was downloaded from the source, check if it already exists in the source.
        #If it does, don't add it.
        if label["name"] not in existing_labels:
            label_prime = {"name": label["name"], "color": label["color"]}
            r = post_req(url, json.dumps(label_prime), credentials)
            status = check_res(r)
