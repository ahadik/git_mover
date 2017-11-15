import requests, json, argparse, sys

#Test if a response object is valid
def check_res(r):
    #if the response status code is a failure (outside of 200 range)
    if r.status_code < 200 or r.status_code >= 300:
        #print the status code and associated response. Return false
        print "STATUS CODE: "+str(r.status_code)
        print "ERROR MESSAGE: "+r.text
        #if error, return False
        return False
    #if successful, return True
    return True

'''
INPUT: an API endpoint for retrieving data
OUTPUT: the request object containing the retrieved data for successful requests. If a request fails, False is returnedself.
'''
def get_req(url, credentials, accept_content_type = 'application/json'):
    r = requests.get(url=url, auth=(credentials['user_name'], credentials['token']), headers={'Content-type': 'application/json', "Accept": accept_content_type})
    return r

'''
INPUT: an API endpoint for posting data
OUTPUT: the request object containing the posted data response for successful requests. If a request fails, False is returnedself.
'''
def post_req(url, data, credentials, accept_content_type = 'application/vnd.github.v3.html+json'):
    r = requests.post(url=url, data=data, auth=(credentials['user_name'], credentials['token']), headers={'Content-type': 'application/json', 'Accept': accept_content_type})
    return r

'''
INPUT:
    source_url: the root url for the GitHub API
    source: the team and repo '<team>/<repo>' to retrieve milestones from
OUTPUT: retrieved milestones sorted by their number if request was successful. False otherwise
'''
def download_milestones(source_url, source, credentials):
	print "Downloading milestones"
    url = source_url+"repos/"+source+"/milestones?filter=all"
    r = get_req(url, credentials)
    status = check_res(r)
    if status:
        #if the request succeeded, sort the retrieved milestones by their number
        sorted_milestones = sorted(json.loads(r.text), key=lambda k: k['number'])
        return sorted_milestones
    return False

'''
INPUT:
    source_url: the root url for the GitHub API
    source: the team and repo '<team>/<repo>' to retrieve issues from
OUTPUT: retrieved issues sorted by their number if request was successful. False otherwise
'''
def download_issues(source_url, source, credentials):
	print "Downloading issues"
    url = source_url+"repos/"+source+"/issues?filter=all"
    r = get_req(url, credentials)
    status = check_res(r)
    if status:
        #if the requests succeeded, sort the retireved issues by their number
        sorted_issues = sorted(json.loads(r.text), key=lambda k: k['number'])
        return sorted_issues
    return False

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
    source_url: the root url for the GitHub API
    source: the team and repo '<team>/<repo>' to retrieve labels from
OUTPUT: retrieved projects if request was successful. False otherwise
'''
def download_projects(source_url, source, credentials):
	print "Downloading projects"
    url = source_url+"repos/"+source+"/projects?filter=all"
    r = get_req(url, credentials, "application/vnd.github.inertia-preview+json")
    status = check_res(r)
    if status:
		 #if the requests succeeded, sort the retireved projects by their number
        sorted_projects = sorted(json.loads(r.text), key=lambda k: k['number'])
        return sorted_projects
    return False

def download_project_columns(source_url, source, credentials, project_id):
	print "Downloading columns for project"
	url = source_url+"projects/"+project_id+"/columns"
    r = get_req(url, credentials, "application/vnd.github.inertia-preview+json")
    status = check_res(r)
    if status:
         #if the requests succeeded, sort the retireved project columns by their number
        sorted_columns = sorted(json.loads(r.text), key=lambda k: k['number'])
        return sorted_columns
    return False

def download_column_cards(source_url, source, credentials, column_id):
	print "Downloading cards for project column"
	url = source_url+"projects/columns/"+columns_id+"/cards"
    r = get_req(url, credentials, "application/vnd.github.inertia-preview+json")
    status = check_res(r)
    if status:
        return json.loads(r.text)
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
            #map the original source milestone's number to the newly created milestone's number
            milestone_map[milestone['number']] = returned_milestone['number']
        else:
            print status
    return milestone_map

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
    for issue in issues:
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
		else:
			returned_issue = json.loads(r.text)
			issue_map[issue['number']] = returned_issue['number']
	
	return issue_map

def create_projects(projects, destination_url, destination, issue_map, credentials, source):
	print "Creating projects"
    url = destination_url+"repos/"+destination+"/projects"

    for project in projects:
        project_dest = {}
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
			columns = download_project_columns(source.source_url, source.source, source.credentials, project["id"])
			if not columns:
				continue
			else:
				create_project_columns(columns, returned_project['id'], destination_url, destination, credentials, issue_map, source)

				

def create_project_columns(columns, project_id, destination_url, destination, credentials, issue_map, source):
	print "Creating columns"
	url = destination_url + "repos/"+destination+"/projects/"+project_id+"/columns"
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
			cards = download_column_cards(source.source_url, source.source, source.credentials, column["id"])
			if not cards:
				continue
			else:
				create_column_cards(cards, returned_column["id", destination_url, destination, credentials, issue_map, source])

def create_column_cards(cards, column_id, destination_url, destination, credentials, issue_map, source):
	print "Creating cards"
	url = destination_url + "repos/"+destination+"/projects/columns/"+column_id+"/cards"
	for card in cards:
		cart_dest = {}
		cart_dest["name"] = card["name"]
		if cart["content_url"]:
			cart_dest["content_url"] = get_cart_content_url(cart["content_url"], destination_url, destination, issue_map, source)
		
		r = post_req(url, json.dumps(cart_dest), credentials, "application/vnd.github.inertia-preview+json")
		status = check_res(r)
		if not status:
            #get the message from the response
            message = json.loads(r.text)
		else:
			print "Cart created"

def get_cart_content_url(cart_content_url, destination_url, destination, issue_map, source):
	replacements = {source.source_url: destination_url, source.source: destination}
	new_repo_address = reduce(lambda a, kv: a.replce(*kv, replacements, cart_content_url))

	splitted_content_url = new_repo_address.split("/")
	splitted_content_url_len = len(splitted_content_url)
	# replace old issue number with new one
	splitted_content_url[splitted_content_url_len - 1] = issue_map[splitted_content_url[splitted_content_url_len - 1]]

	return "/".join(splitted_content_url)

def main():
    parser = argparse.ArgumentParser(description='Migrate Milestones, Labels, and Issues between two GitHub repositories. To migrate a subset of elements (Milestones, Labels, Issues), use the element specific flags (--milestones, --lables, --issues). Providing no flags defaults to all element types being migrated.')
    parser.add_argument('user_name', type=str, help='Your GitHub (public or enterprise) username: name@email.com')
    parser.add_argument('token', type=str, help='Your GitHub (public or enterprise) personal access token')
    parser.add_argument('source_repo', type=str, help='the team and repo to migrate from: <team_name>/<repo_name>')
    parser.add_argument('destination_repo', type=str, help='the team and repo to migrate to: <team_name>/<repo_name>')
    parser.add_argument('--destinationToken', '-dt', nargs='?', type=str, help='Your personal access token for the destination account, if you are migrating between GitHub installations')
    parser.add_argument('--destinationUserName', '-dun', nargs='?', type=str, help='Username for destination account, if you are migrating between GitHub installations')
    parser.add_argument('--sourceRoot', '-sr', nargs='?', default='https://api.github.com', type=str, help='The GitHub domain to migrate from. Defaults to https://www.github.com. For GitHub enterprise customers, enter the domain for your GitHub installation.')
    parser.add_argument('--destinationRoot', '-dr', nargs='?', default='https://api.github.com', type=str, help='The GitHub domain to migrate to. Defaults to https://www.github.com. For GitHub enterprise customers, enter the domain for your GitHub installation.')
    parser.add_argument('--milestones', '-m', action="store_true", help='Toggle on Milestone migration.')
    parser.add_argument('--labels', '-l', action="store_true", help='Toggle on Label migration.')
    parser.add_argument('--issues', '-i', action="store_true", help='Toggle on Issue migration.')
    parser.add_argument('--projects', '-p', action="store_true", help='Toggle on Projects migration.')
    parser.add_argument('--pull_requests', '-pr', action="store_true", help='Toggle on Pull Requests migration.')
	parser.add_argument('--forceAssignee', '-fa', action="store_true", help='Force assignees between repositories.')
	
    args = parser.parse_args()

    destination_repo = args.destination_repo
    source_repo = args.source_repo
    source_credentials = {'user_name' : args.user_name, 'token' : args.token}

    if (args.sourceRoot != 'https://api.github.com'):
        args.sourceRoot += '/api/v3'

    if (args.destinationRoot != 'https://api.github.com'):
        args.destinationRoot += '/api/v3'

    if (args.sourceRoot != args.destinationRoot):
        if not (args.destinationToken):
            sys.stderr.write("Error: Source and Destination Roots are different but no token was supplied for the destination repo.")
            quit()

    if not (args.destinationUserName):
        print('No destination User Name provided, defaulting to source User Name: '+args.user_name)
        args.destinationUserName = args.user_name

    destination_credentials = {'user_name': args.destinationUserName, 'token': args.destinationToken}

    source_root = args.sourceRoot+'/'
    destination_root = args.destinationRoot+'/'

    milestone_map = None

    if args.milestones == False and args.labels == False and args.issues == False and args.projects == False and args.pull_requests == False:
        args.milestones = True
        args.labels = True
        args.issues = True
        args.projects = True
        args.pull_requests = True

	if args.projects == True or args.pull_requests == True:
		args.issues = True

    if args.milestones:
        milestones = download_milestones(source_root, source_repo, source_credentials)
        if milestones:
            milestone_map = create_milestones(milestones, destination_root, destination_repo, destination_credentials)
        elif milestones == False:
            sys.stderr.write('ERROR: Milestones failed to be retrieved. Exiting...')
            quit()
        else:
            print "No milestones found. None migrated"

    if args.labels:
        labels = download_labels(source_root, source_repo, source_credentials)
        if labels:
            create_labels(labels, destination_root, destination_repo, destination_credentials)
        elif labels == False:
            sys.stderr.write('ERROR: Labels failed to be retrieved. Exiting...')
            quit()
        else:
            print "No Labels found. None migrated"

    if args.issues:
        issues = download_issues(source_root, source_repo, source_credentials)
        if issues:
            sameInstall = False
            if (args.sourceRoot == args.destinationRoot || args.forceAssignee):
                sameInstall = True
            issue_map = create_issues(issues, destination_root, destination_repo, args.milestones, args.labels, milestone_map, destination_credentials, sameInstall)
        elif issues == False:
            sys.stderr.write('ERROR: Issues failed to be retrieved. Exiting...')
            quit()
        else:
            print "No Issues found. None migrated"
    else:
        issues = False

    if args.projects and issues != False:
        projects = download_projects(source_root, source_repo, source_credentials)
        if projects:
            create_projects(projects, destination_root, destination_repo, issue_map, destination_credentials, {
				source_url: source_root, 
				source: source_repo, 
				credentials: source_credentials
			})
        elif projects == False:
            sys.stderr.write("ERROR: Projects failed to be retrievied. Exiting...")
            quit()
        else:
            print "No Projects found. None migrated"

if __name__ == "__main__":
    main()
