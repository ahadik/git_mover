import json
from libs import *
from movers.issue_comments import create_issue_comments, download_issue_comments, create_review_comments

def process_pull_request(issue, source_credentials, credentials, destination_url, destination, milestones, labels, milestone_map):
    print "Processing PR"
    pull_request_data = issue.get("pull_request")
    pull_request = get_data(pull_request_data.get("url"), source_credentials)
    if not pull_request:
        return False
    else:
        return create_pull_request(pull_request, source_credentials, credentials, destination_url, destination, milestones, labels, milestone_map, issue)

def download_pull_request(pull_request_url, credentials):
    print "Getting source PR"
    return get_data(pull_request_url, credentials)

def create_pull_request(pull_request, source_credentials, credentials, destination_url, destination, milestones, labels, milestone_map, issue):
    if not is_branch_exists(pull_request["head"]["ref"], credentials, destination_url, destination):
        return False

    url = destination_url+"repos/"+destination+"/pulls"

    pull_request_dest = {}
    pull_request_dest["title"] = pull_request["title"]
    pull_request_dest["head"] = get_pr_userspace(pull_request["head"])
    pull_request_dest["base"] = pull_request["base"]["ref"]
    pull_request_dest["body"] = "[Original PR](%s); %s" % (pull_request["html_url"], add_user_to_text(pull_request["user"]["login"], pull_request["body"]))

    print "Creating PR"
    r = post_req(url, json.dumps(pull_request_dest), credentials)
    status = check_res(r)
    
    #if adding the pull_request failed
    if not status:
        print "Creation of pull request failed (%d)" % int(pull_request["number"])
        return False
    
    returned_pull_request = json.loads(r.text)
    print "PR created with number " + str(returned_pull_request["number"])

    set_reviewers_for_pr(returned_pull_request, pull_request, source_credentials, credentials)
    
    if pull_request.get("comments", 0) > 0:
        print "Adding PR comments"
        issue_comments = get_data(pull_request.get("comments_url"), source_credentials)
        create_issue_comments(issue_comments, returned_pull_request.get("comments_url"), credentials)

    if pull_request.get("review_comments", 0) > 0:
        print "Adding PR review comments"
        source_pr_reviews = get_pr_reviews(pull_request.get("url"), source_credentials)
        review_comments_url = pull_request.get("review_comments_url") + "?sort=created&direction=asc"
        review_comments = get_data(review_comments_url, source_credentials)
        create_review_comments(review_comments, returned_pull_request.get("review_comments_url"), credentials, source_pr_reviews)

    update_pr_issue(returned_pull_request, pull_request, credentials, milestones, labels, milestone_map, issue)
    # update state with current value
    pull_request_dest["state"] = pull_request["state"]
    patch_req(returned_pull_request["url"], json.dumps(pull_request_dest), credentials)

    print "PR created %d -> %d" % (int(pull_request["number"]), int(returned_pull_request.get("number")))

    return returned_pull_request.get("number")

def get_pr_userspace(source_data):
    source_user_login = source_data["user"]["login"]
    source_label = source_data["label"]

    return source_label.replace(source_user_login, get_destination_username(source_user_login))

def get_reviewers(reviewers):
    local_reviewers = []
    for reviewer in reviewers:
        local_reviewers.append(get_destination_username(reviewer["login"]))
    
    return local_reviewers

def is_branch_exists(branch_name, credentials, destination_url, destination):
    if branch_name == "master":
        return False

    print "Checking is branch '%s' exists..." % branch_name

    url = destination_url+"repos/"+destination+"/branches/" + branch_name
    r = get_req(url, credentials)
    status = check_res(r)

    if status:
        return True
    else:
        return False

def update_pr_issue(returned_pull_request, pull_request, credentials, milestones, labels, milestone_map, source_issue_data):
    # get state and labels for PR Issue
    issue_data = get_data(returned_pull_request["_links"]["issue"]["href"], credentials)
    if pull_request.get("state", "open") == "closed":
        print "Closing PR"
        issue_data["state"] = "closed"
    if labels and source_issue_data.get("labels", False):
        print "Adding labels"
        issue_data["labels"] = source_issue_data.get("labels")
    if milestones and source_issue_data.get("milestone", False) and source_issue_data["milestone"] != None and milestone_map:
        #if the milestone associated with the issue is in the milestone map
        if milestone_map.get(source_issue_data['milestone']['number'], False):
            print "Adding milestone"
            #set the milestone value of the new issue to the updated number of the migrated milestone
            issue_data["milestone"] = milestone_map[source_issue_data["milestone"]["number"]]
     # assign user if exists
    if (pull_request.get("assignee", False)):
        print "Adding assingees"
        issue_data["assignees"] = [get_destination_username(pull_request["assignee"]["login"]),]

    print "Updating PR Issue"
    patch_req(issue_data["url"], json.dumps(issue_data), credentials)

def get_pr_reviews(source_pr_url, credentials):
    source_pr_reviews_url = source_pr_url + "/reviews"
    source_reviews = get_data(source_pr_reviews_url, credentials)
    
    if source_reviews:
        reviews = {}
        for review in source_reviews:
            review_skeleton = {}
            review_skeleton["user"] = get_destination_username(review["user"]["login"])
            review_skeleton["body"] = add_user_to_text(review["user"]["login"], review["body"])
            review_skeleton["state"] = review["state"]
            review_skeleton["commit_id"] = review["commit_id"]
            reviews[int(review.get("id"))] = review_skeleton

        return reviews
    else:
        return False

def set_reviewers_for_pr(returned_pull_request, pull_request, source_credentials, credentials):
    source_reviewers_url = pull_request.get("url") + "/requested_reviewers"
    source_reviewers = get_data(source_reviewers_url, source_credentials, 'application/vnd.github.thor-preview+json')
    if source_reviewers and len(source_reviewers.get("users")) > 0:
        print "Collectin source reviewers"
        request_for_reviewers = []
        for source_reviewer in source_reviewers.get("users"):
            request_for_reviewers.append(get_destination_username(source_reviewer.get("login")))

        if len(request_for_reviewers) > 0:
            print "Creating destination PR reviewers"
            dest_reviewers_url = returned_pull_request.get("url") + "/reviewers"
            data = {
                "reviewers": request_for_reviewers
            }
            r = post_req(dest_reviewers_url, json.dumps(data), credentials, 'application/vnd.github.thor-preview+json')
            status = check_res(r)
    
            #if adding the pull_request failed
            if not status:
                print "Creating of reviewers for PR %d failed" % int(returned_pull_request.get("number"))
