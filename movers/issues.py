import json, sys
from libs import *
from movers.issue_comments import create_issue_comments, download_issue_comments
from movers.pull_requests import process_pull_request

'''
INPUT:
    source_url: the root url for the GitHub API
    source: the team and repo '<team>/<repo>' to retrieve issues from
OUTPUT: retrieved issues sorted by their number if request was successful. False otherwise
'''
def download_issues(source_url, source, credentials):
    print "Downloading issues"
    page_number = 1
    per_page = 50
    url = source_url+"repos/"+source+"/issues?filter=all&state=all&direction=asc&page=%d&per_page=%d"
    sorted_issues = []
    while True:
        print "Checking page %d" % page_number
        current_page_url = url % (page_number, per_page)
        data = get_data(current_page_url, credentials)
        if data:
            #if the requests succeeded, sort the retireved issues by their number
            sorted_issues += sorted(data, key=lambda k: k['number'])

            if len(data) < per_page:
                break

            page_number += 1            
        else:
            break

    print "Found %d issues" % len(sorted_issues)
    return sorted_issues

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
def create_issues(issues, destination_url, destination, milestones, labels, milestone_map, source_credentials, credentials, same_install):
    print "Creating issues"
    url = destination_url+"repos/"+destination+"/issues"

    current_issues = download_issues(destination_url, destination, credentials)

    issue_map = {}
    for issue in issues:
        issue_number = issue_exists(issue, current_issues)

        if issue_number:
            issue_map[int(issue['number'])] = int(issue_number)
            print "Issue exists, getting next one. Matched numbers: %d -> %d" % (int(issue['number']), int(issue_number))
            continue

        if issue.get("pull_request", False):
            print "This is Issue created for pull request ("+str(issue["number"])+")"
            pull_request_number = process_pull_request(issue, source_credentials, credentials, destination_url, destination, milestones, labels, milestone_map)
            if pull_request_number:
                issue_map[int(issue['number'])] = int(pull_request_number)
            
            continue

        #create a new issue object containing only the data necessary for the creation of a new issue
        issue_prime = {"title" : issue["title"], "body" : get_issue_body(issue)}

        if (issue.get("assignee", False) and same_install):
            assignee = get_destination_username(issue["assignee"]["login"])
            issue_prime["assignees"] = [assignee,]

        #if milestones were migrated and the issue to be posted contains milestones
        if milestones and issue.get("milestone", False) and issue["milestone"] != None:
            #if the milestone associated with the issue is in the milestone map
            if milestone_map and milestone_map.get(issue['milestone']['number'], False):
                #set the milestone value of the new issue to the updated number of the migrated milestone
                issue_prime["milestone"] = milestone_map[issue["milestone"]["number"]]

        #if labels were migrated and the issue to be migrated contains labels
        if labels and issue.get("labels", False):
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

        if issue.get("comments", 0) > 0:
            issue_comments = download_issue_comments(issue.get("comments_url"), source_credentials)
            create_issue_comments(issue_comments, returned_issue.get("comments_url"), credentials)

        print("update state with current value")
        issue_prime["state"] = issue["state"]
        patch_req(returned_issue.get("url"), json.dumps(issue_prime), credentials)

        issue_map[int(issue['number'])] = int(returned_issue['number'])
        print "Matched numbers: %d -> %d" % (int(issue['number']), int(returned_issue['number']))

    return issue_map

def issue_exists(issue, current_issues):
    flatten_examine_issue = make_flat_issue(issue)
    for current_issue in current_issues:
        if make_flat_issue(current_issue) == flatten_examine_issue:
            return current_issue["number"]

    return False

def make_flat_issue(issue_dict):
    flatten_issue = issue_dict["state"] + issue_dict["title"] + issue_dict["body"]
    flatten_issue += str(issue_dict["comments"])

    if issue_dict.get("pull_request", False):
        flatten_issue += "pull_request"

    return flatten_issue

def get_issue_body(issue):
    return "[Original issue](%s); %s" % (issue["html_url"], add_user_to_text(issue["user"]["login"], issue["body"]))
