import json
from libs import *

def download_issue_comments(comments_url, credentials):
    print "Getting comments for issue"
    return get_data(comments_url, credentials)

def create_issue_comments(issue_comments, issue_comment_url, credentials):
    if not issue_comments:
        return False

    print "Creating comments for issue"
    for issue_comment in issue_comments:
        issue_comment_dest = {
            "body": add_user_to_text(issue_comment["user"]["login"], issue_comment["body"])
        }

        r = post_req(issue_comment_url, json.dumps(issue_comment_dest), credentials)
        status = check_res(r)

        if not status:
            #get the message from the response
            message = json.loads(r.text)
            continue

def create_review_comments(review_comments, review_comment_url, credentials, source_pr_reviews):
    if not review_comments:
        return False

    comments_map = {}

    for review_comment in review_comments:
        print "Creating review comment for pull request"
        print "Source comment ID: %d" % int(review_comment.get("id"))
        review_comment_desc = {
            "body": add_user_to_text(review_comment["user"]["login"], review_comment["body"])
        }

        if review_comment.get("in_reply_to_id", False) and comments_map.get(review_comment.get("in_reply_to_id", 0), False):
            review_comment_desc["in_reply_to_id"] = comments_map[review_comment.get("in_reply_to_id")]
        else:
            review_comment_desc["commit_id"] = review_comment["commit_id"]
            review_comment_desc["path"] = review_comment["path"]
            if review_comment.get("position", None) != None:
                review_comment_desc["position"] = int(review_comment.get("position"))

        r = post_req(review_comment_url, json.dumps(review_comment_desc), credentials)

        status = check_res(r)
        message = json.loads(r.text)

        if not status:
            #get the message from the response
            continue
        else:
            print "New comment ID: %d" % int(message.get("id"))
            comments_map[review_comment.get("id")] = int(message.get("id"))
            processed_source_pr_reviews = update_review(message, credentials, review_comment.get("pull_request_review_id"), source_pr_reviews)

            process_reviews(message.get("pull_request_url"), processed_source_pr_reviews, credentials)

def update_review(message, credentials, source_pr_review_id, source_pr_reviews):
    dest_pr_review_url = message.get("pull_request_url") + "/reviews/%d" % int(message.get("pull_request_review_id"))
    dest_pr_review = get_data(dest_pr_review_url, credentials)
    if dest_pr_review:
        print "Updating review for review comment"
        source_pr_review = source_pr_reviews.get(int(source_pr_review_id))
        dest_pr_review["state"] = source_pr_review["state"]
        dest_pr_review["body"] = source_pr_review["body"]

        r = post_req(dest_pr_review_url + "/events", json.dumps(dest_pr_review), credentials)
        status = check_res(r)
        message = json.loads(r.text)

        if status:
            source_pr_reviews[source_pr_review_id] = None

    return source_pr_reviews

def process_reviews(dest_pr_url, source_reviews, credentials):
    for key, value in source_reviews.iteritems():
        if value == None:
            continue

        event = get_review_event(value["state"])
        if not event:
            continue
        
        dest_review = {}
        dest_review["commit_id"] = value["commit_id"]
        dest_review["body"] = value["body"]
        dest_review["event"] = event

        r = post_req(dest_pr_url + "/reviews", json.dumps(dest_review), credentials)
        status = check_res(r)
        message = json.loads(r.text)

        if not status:
            print "FAILED: create review for PR %s " % dest_pr_url

def get_review_event(state):
    if state == "APPROVED":
        return "APPROVE"
    elif state == "CHANGES_REQUESTED":
        return "REQUEST_CHANGES"
    elif state == "COMMENTED":
        return "COMMENT"
    else:
        return False
