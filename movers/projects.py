import json
from libs import *

'''
INPUT:
    source_url: the root url for the GitHub API
    source: the team and repo '<team>/<repo>' to retrieve labels from
OUTPUT: retrieved projects if request was successful. False otherwise
'''
def download_projects(source_url, source, credentials):
    print "Downloading projects"
    url = source_url+"repos/"+source+"/projects?filter=all&state=all"
    data = get_data(url, credentials, "application/vnd.github.inertia-preview+json")
    if data:
        #if the requests succeeded, sort the retireved projects by their number
        return sorted(json.loads(data), key=lambda k: k['number'])
    else:
        return False

def download_project_columns(url, credentials):
    print "Downloading columns for project"
    return get_data(url, credentials, "application/vnd.github.inertia-preview+json")

def download_column_cards(url, credentials):
    print "Downloading cards for project column"
    return get_data(url, credentials, "application/vnd.github.inertia-preview+json")

def create_projects(projects, destination_url, destination, issue_map, credentials, source):
    print "Creating projects"
    print "Issue Map: "
    print issue_map

    url = destination_url+"repos/"+destination+"/projects"

    for project in projects:
        project_dest = {"creator": {}}
        project_dest["name"] = project["name"]
        project_dest["body"] = add_user_to_text(project["creator"]["login"], project["body"])
        r = post_req(url, json.dumps(project_dest), credentials, "application/vnd.github.inertia-preview+json")
        status = check_res(r)
        if not status:
            #get the message from the response
            message = json.loads(r.text)
        else:
            returned_project = json.loads(r.text)
            project_dest["state"] = project["state"]
            # update project state
            patch_req(returned_project.get("url"), json.dumps(project_dest), credentials)

            columns = download_project_columns(project["columns_url"], source["credentials"])
            if not columns:
                continue
            else:
                create_project_columns(columns, returned_project['id'], destination_url, credentials, issue_map, source)

def create_project_columns(columns, project_id, destination_url, credentials, issue_map, source):
    print "Creating columns"
    url = destination_url + "projects/"+str(project_id)+"/columns"
    for column in columns:
        column_dest = {}
        column_dest["name"] = column["name"]
        r = post_req(url, json.dumps(column_dest), credentials, "application/vnd.github.inertia-preview+json")
        status = check_res(r)
        if not status:
            #get the message from the response
            message = json.loads(r.text)
        else:
            print "Column created"
            returned_column = json.loads(r.text)
            cards = download_column_cards(column["cards_url"], source["credentials"])
            if not cards:
                continue
            else:
                create_column_cards(cards, returned_column["id"], destination_url, credentials, issue_map)

def create_column_cards(cards, column_id, destination_url, credentials, issue_map):
    print "Creating cards"
    url = destination_url + "projects/columns/"+str(column_id)+"/cards"
    for card in cards:
        card_dest = {"creator": {}}
        card_dest["note"] = card["note"]
        card_dest["creator"]["login"] = card["creator"]["login"]
        if card.get("content_url", False):
            content_id = get_card_content_id(card["content_url"], issue_map)
            if content_id:
                card_dest["content_id"] = content_id
                card_dest["content_type"] = "Issue"
        
        if card_dest.get("note", False) or card_dest.get("content_id", False):
            r = post_req(url, json.dumps(card_dest), credentials, "application/vnd.github.inertia-preview+json")
            status = check_res(r)
            if not status:
                #get the message from the response
                message = json.loads(r.text)
            else:
                print "Card created"
        else:
            print "Cannot create cart without note AND content_id"

def get_card_content_id(card_content_url, issue_map):
    splitted_content_url = card_content_url.split("/")
    content_id = int(splitted_content_url[-1])
    # replace old issue number with new one
    if issue_map.get(content_id, False):
        print "Getting " + str(issue_map[content_id]) + " for " + str(content_id)
        return issue_map[content_id]
    else:
        print "Issue with number "+str(content_id)+" not found in map"
        return None