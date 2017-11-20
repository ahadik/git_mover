import json
from libs import *

'''
INPUT:
    source_url: the root url for the GitHub API
    source: the team and repo '<team>/<repo>' to retrieve milestones from
OUTPUT: retrieved milestones sorted by their number if request was successful. False otherwise
'''
def download_milestones(source_url, source, credentials):
    print "Downloading milestones"
    url = source_url+"repos/"+source+"/milestones?filter=all&state=all"
    data = get_data(url, credentials)
    if data:
        #if the request succeeded, sort the retrieved milestones by their number
        return sorted(data, key=lambda k: k['number'])
    else:
        return False

'''
INPUT:
    milestones: python list of dicts containing milestone info to be POSTED to GitHub
    destination_url: the root url for the GitHub API
    destination: the team and repo '<team>/<repo>' to post milestones to
OUTCOME: Post milestones to GitHub
OUTPUT: A dict of milestone numbering that maps from source milestone numbers to destination milestone numbers
'''
def create_milestones(milestones, destination_url, destination, credentials):
    print "Creating milestones"
    url = destination_url+"repos/"+destination+"/milestones"
    milestone_map = {}
    for milestone in milestones:
        #create a new milestone that includes only the attributes needed to create a new milestone
        milestone_prime = {"title": milestone["title"], "state": milestone["state"], "description": milestone["description"], "due_on": milestone["due_on"]}
        r = post_req(url, json.dumps(milestone_prime), credentials)
        status = check_res(r)
        if status:
            #if the POST request succeeded, parse and store the new milestone returned from GitHub
            returned_milestone = json.loads(r.text)
            #map the source milestone's number to the newly created milestone's number
            milestone_map[milestone['number']] = returned_milestone['number']
        else:
            print status

    return milestone_map
