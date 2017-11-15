import json
from libs import *

'''
INPUT:
    source_url: the root url for the GitHub API
    source: the team and repo '<team>/<repo>' to retrieve issues from
OUTPUT: retrieved issues sorted by their number if request was successful. False otherwise
'''
def download_issues(source_url, source, credentials):
    print "Downloading issues"

    url = source_url+"repos/"+source+"/issues?filter=all&state=all"
    r = get_req(url, credentials)
    status = check_res(r)
    if status:
        #if the requests succeeded, sort the retireved issues by their number
        sorted_issues = sorted(json.loads(r.text), key=lambda k: k['number'])
        return sorted_issues
    return False

'''
INPUT:
    issues: python list of dicts containing issue info to be POSTED to GitHub
    destination_url: the root url for the GitHub API
    destination_urlination: the team and repo '<team>/<repo>' to post issues to
    milestones: a boolean flag indicating that milestones were included in this migration
    labels: a boolean flag indicating that labels were included in this migration
OUTCOME: Post issues to GitHub
OUTPUT: Null
'''
def create_issues(issues, destination_url, destination, milestones, labels, milestone_map, credentials, sameInstall):
    print "Creating issues"
    url = destination_url+"repos/"+destination+"/issues"

    current_issues = download_issues(destination_url, destination, credentials)

    issue_map = {}
    for issue in issues:
        issue_number = issue_exists(issue, current_issues)
        if issue_number:
            issue_map[issue['number']] = issue_number
            print "Issue exists, getting next one"
            continue

        #create a new issue object containing only the data necessary for the creation of a new issue
        assignee = None
        if (issue["assignee"] and sameInstall):
            assignee = issue["assignee"]["login"]
        issue_prime = {"title" : issue["title"], "body" : issue["body"], "assignee": assignee, "state" : issue["state"]}
        #if milestones were migrated and the issue to be posted contains milestones
        if milestones and "milestone" in issue and issue["milestone"]!= None:
            #if the milestone associated with the issue is in the milestone map
            if issue['milestone']['number'] in milestone_map:
                #set the milestone value of the new issue to the updated number of the migrated milestone
                issue_prime["milestone"] = milestone_map[issue["milestone"]["number"]]
        #if labels were migrated and the issue to be migrated contains labels
        if labels and "labels" in issue:
            issue_prime["labels"] = issue["labels"]
        r = post_req(url, json.dumps(issue_prime), credentials)
        status = check_res(r)
        #if adding the issue failed
        if not status:
            #get the message from the response
            message = json.loads(r.text)
            #if the error message is for an invalid entry because of the assignee field, remove it and repost with no assignee
            if message['errors'][0]['code'] == 'invalid' and message['errors'][0]['field'] == 'assignee':
                sys.stderr.write("WARNING: Assignee "+message['errors'][0]['value']+" on issue \""+issue_prime['title']+"\" does not exist in the destination repository. Issue added without assignee field.\n\n")
                issue_prime.pop('assignee')
                post_req(url, json.dumps(issue_prime), credentials)
            continue

        returned_issue = json.loads(r.text)
        issue_map[issue['number']] = returned_issue['number']

    return issue_map

def issue_exists(issue, current_issues):
    flatten_examine_issue = make_flat_issue(issue)
    for current_issue in current_issues:
        if make_flat_issue(current_issue) == flatten_examine_issue:
            return current_issue["number"]

    return False

def make_flat_issue(issue_dict):
    flatten_issue = ""
    flatten_issue += issue_dict["state"] + issue_dict["title"] + issue_dict["body"] + issue_dict["user"]["login"]
    flatten_issue += str(issue_dict["comments"])

    if "pull_request" in issue_dict:
        flatten_issue += "pull_request"
    
    return flatten_issue
