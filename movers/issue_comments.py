import json, sys
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

def create_review_comments(review_comments, review_comment_url, credentials):
    if not review_comments:
        return False

    print "Creating review comment for pull request"
    print "PR review comment url: %s" % review_comment_url

    comments_map = {}

    for review_comment in review_comments:
        review_comment_desc = {
            "body": add_user_to_text(review_comment["user"]["login"], review_comment["body"])
        }

        if review_comment.get("in_reply_to_id", False) and comments_map[review_comment.get("in_reply_to_id")] != None:
            review_comment_desc["in_reply_to_id"] = comments_map[review_comment.get("in_reply_to_id")]
        else:
            review_comment_desc["commit_id"] = review_comment["commit_id"]
            review_comment_desc["path"] = review_comment["path"]
            review_comment_desc["position"] = review_comment["position"]


        r = post_req(review_comment_url, json.dumps(review_comment_desc), credentials)

        status = check_res(r)
        message = json.loads(r.text)

        if not status:
            #get the message from the response
            continue
        else:
            comments_map[review_comment.get("id")] = message.get("id")
