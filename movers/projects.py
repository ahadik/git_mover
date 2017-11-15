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
    r = get_req(url, credentials, "application/vnd.github.inertia-preview+json")
    status = check_res(r)
    if status:
            #if the requests succeeded, sort the retireved projects by their number
        sorted_projects = sorted(json.loads(r.text), key=lambda k: k['number'])
        return sorted_projects
    return False

def download_project_columns(url, credentials, project_id):
    print "Downloading columns for project"
    r = get_req(url, credentials, "application/vnd.github.inertia-preview+json")
    status = check_res(r)
    if status:
            #if the requests succeeded, sort the retireved project columns by their number
        return json.loads(r.text)
    return False

def download_column_cards(url, credentials, column_id):
    print "Downloading cards for project column"
    r = get_req(url, credentials, "application/vnd.github.inertia-preview+json")
    status = check_res(r)
    if status:
        return json.loads(r.text)
    return False

def create_projects(projects, destination_url, destination, issue_map, credentials, source):
    print "Creating projects"
    url = destination_url+"repos/"+destination+"/projects"

    for project in projects:
        project_dest = {"creator": {}}
        project_dest["name"] = project["name"]
        project_dest["body"] = project["body"]
        project_dest["state"] = project["state"]
        project_dest["creator"]["login"] = project["creator"]["login"]
        r = post_req(url, json.dumps(project_dest), credentials, "application/vnd.github.inertia-preview+json")
        status = check_res(r)
        if not status:
            #get the message from the response
            message = json.loads(r.text)
        else:
            returned_project = json.loads(r.text)
            columns = download_project_columns(project["columns_url"], source["credentials"], project["id"])
            if not columns:
                continue
            else:
                create_project_columns(columns, returned_project['id'], destination_url, destination, credentials, issue_map, source)

def create_project_columns(columns, project_id, destination_url, destination, credentials, issue_map, source):
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
            cards = download_column_cards(column["cards_url"], source["credentials"], column["id"])
            if not cards:
                continue
            else:
                create_column_cards(cards, returned_column["id"], destination_url, destination, credentials, issue_map, source)

def create_column_cards(cards, column_id, destination_url, destination, credentials, issue_map, source):
    print "Creating cards"
    url = destination_url + "projects/columns/"+str(column_id)+"/cards"
    for card in cards:
        card_dest = {"creator": {}}
        card_dest["note"] = card["note"]
        card_dest["creator"]["login"] = card["creator"]["login"]
        if card["content_url"]:
            card_dest["content_url"] = get_card_content_url(card["content_url"], destination_url, destination, issue_map, source)
        
        r = post_req(url, json.dumps(card_dest), credentials, "application/vnd.github.inertia-preview+json")
        status = check_res(r)
        if not status:
            #get the message from the response
            message = json.loads(r.text)
        else:
            print "Card created"

def get_card_content_url(card_content_url, destination_url, destination, issue_map, source):
    replacements = (source["source_url"], destination_url), (source["source"], destination)
    new_repo_address = reduce(lambda a, kv: a.replace(*kv), replacements, card_content_url)

    splitted_content_url = new_repo_address.split("/")
    splitted_content_url_len = len(splitted_content_url) - 1
    # replace old issue number with new one
    splitted_content_url[splitted_content_url_len] = issue_map[int(splitted_content_url[splitted_content_url_len])]

    return "/".join(splitted_content_url)
