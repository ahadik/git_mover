import requests, json, argparse, sys, tempfile, os, shutil
from urlparse import urlparse

#default constants
ghe_url = 'https://github.2ndsiteinc.com'
ghe_api_path = '/api/v3'
github_url = 'https://github.com'
github_api_url = 'https://api.github.com'

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
def get_req(url, credentials):
	r = requests.get(url=url, auth=(credentials['user_name'], credentials['token']), headers={'Content-type': 'application/json'})
	return r

'''
INPUT: an API endpoint for posting data
OUTPUT: the request object containing the posted data response for successful requests. If a request fails, False is returnedself.
'''
def post_req(url, data, credentials):
	r = requests.post(url=url, data=data, auth=(credentials['user_name'], credentials['token']), headers={'Content-type': 'application/json', 'Accept': 'application/vnd.github.v3.html+json'})
	return r

'''
INPUT:
	source_url: the root url for the GitHub API
	source: the team and repo '<team>/<repo>' to retrieve repository information from
OUTPUT: retrieved repository information.
'''
def download_repository(source_url, source, credentials):
	url = source_url+"repos/"+source
	r = get_req(url, credentials)
	status = check_res(r)
	if status:
		return json.loads(r.text)
	return False

'''
INPUT:
	source_url: the root url for the GitHub API
	source: the team and repo '<team>/<repo>' to retrieve milestones from
OUTPUT: retrieved milestones sorted by their number if request was successful. False otherwise
'''
def download_milestones(source_url, source, credentials):
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
	url = source_url+"repos/"+source+"/labels?filter=all"
	r = get_req(url, credentials)
	status = check_res(r)
	if status:
		return json.loads(r.text)
	return False

'''
INPUT:
	repo: source repository information
	destination_url: the root url for the GitHub API
	destination: the team and repo '<team>/<repo>' to post milestones to
OUTCOME: Post new repository to GitHub
OUTPUT: A dict of new repository information
'''
def create_repository(repo, destination_url, destination, credentials, inheritVisibility):
	destinations = destination.split('/')
	url = destination_url+"orgs/"+destinations[0]+"/repos"
	privateRepo = True if not inheritVisibility else repo['private']
	repository = {"name": destinations[1], "description": repo['description'], 'homepage': repo['homepage'], 'private': privateRepo, 'has_projects': repo['has_projects'], 'auto_init': False}
	print 'create_repository:' + url
	print 'create_repository: json = ' + json.dumps(repository)
	# r = post_req(url, json.dumps(repository), credentials)
	# status = check_res(r)
	# if status:
	# 	#if the POST request succeeded, parse and store the new milestone returned from GitHub
	# 	return json.loads(r.text)
	# else:
	# 	print status
	# return {}

'''
INPUT:
	source_root: source repository information
	source_repo: the root url for the GitHub API
	source_credentials: the team and repo '<team>/<repo>' to post milestones to
OUTCOME: Post new repository to GitHub
OUTPUT: A dict of new repository information
'''
def clone_repository(source_root, source_repo, source_credentials, destination_root, destination_repo, destination_credentials, ssh):
	github_api_host = 'api.github.com'
	source = urlparse(source_root)
	source_host = 'github.com' if source.netloc.lower() == github_api_host else source.netloc[::-1].replace(ghe_api_path[::-1], '' , 1)[::-1]
	sourceUrl = ('git@'+source_host+source.path.replace(ghe_api_path, '', 1))[:-1]+':'+source_repo+'.git'
	if not ssh:
		sourceUrl = source.scheme+'://'+source_credentials['user_name']+':'+source_credentials['token']+'@'+source_host+source.path.replace(ghe_api_path, '', 1)+source_repo+'.git'

	destination = urlparse(destination_root)
	destination_host = 'github.com' if destination.netloc.lower() == github_api_host else destination.netloc[::-1].replace(ghe_api_path[::-1], '' , 1)[::-1]
	destinationUrl = ('git@'+destination_host+destination.path.replace(ghe_api_path, '', 1))[:-1]+':'+destination_repo+'.git'
	if not ssh:
		destinationUrl = destination.scheme+'://'+destination_credentials['user_name']+':'+destination_credentials['token']+'@'+destination_host+destination.path.replace(ghe_api_path, '', 1)+destination_repo+'.git'

	current_directory = os.getcwd()
	temp_dir = tempfile.mkdtemp()
	os.chdir(temp_dir)

	cmd = os.system('git clone --bare '+sourceUrl+' .')
	cmd |= os.system('git push --mirror '+destinationUrl)
	os.chdir(current_directory)
	shutil.rmtree(temp_dir)
	return cmd == 0

'''
INPUT:
	milestones: python list of dicts containing milestone info to be POSTED to GitHub
	destination_url: the root url for the GitHub API
	destination: the team and repo '<team>/<repo>' to post milestones to
OUTCOME: Post milestones to GitHub
OUTPUT: A dict of milestone numbering that maps from source milestone numbers to destination milestone numbers
'''
def create_milestones(milestones, destination_url, destination, credentials):
	url = destination_url+"repos/"+destination+"/milestones"
	milestone_map = {}
	for milestone in milestones:
		#create a new milestone that includes only the attributes needed to create a new milestone
		milestone_prime = {"title": milestone["title"], "state": milestone["state"], "description": milestone["description"], "due_on": milestone["due_on"]}
		print 'Create Milestones: ' + url
		print 'Create Milestones: json ' + json.dumps(milestone_prime)
		# r = post_req(url, json.dumps(milestone_prime), credentials)
		# status = check_res(r)
		# if status:
		# 	#if the POST request succeeded, parse and store the new milestone returned from GitHub
		# 	returned_milestone = json.loads(r.text)
		# 	#map the original source milestone's number to the newly created milestone's number
		# 	milestone_map[milestone['number']] = returned_milestone['number']
		# else:
		# 	print status
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
			print 'Create labels: ' + url
			print 'Create labels: json ' + json.dumps(label_prime)
			# r = post_req(url, json.dumps(label_prime), credentials)
			# status = check_res(r)

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
		print 'Create issue: ' + url
		print 'Create issue: json ' + json.dumps(issue_prime)
		# r = post_req(url, json.dumps(issue_prime), credentials)
		# status = check_res(r)
		# #if adding the issue failed
		# if not status:
		# 	#get the message from the response
		# 	message = json.loads(r.text)
		# 	#if the error message is for an invalid entry because of the assignee field, remove it and repost with no assignee
		# 	if message['errors'][0]['code'] == 'invalid' and message['errors'][0]['field'] == 'assignee':
		# 		sys.stderr.write("WARNING: Assignee "+message['errors'][0]['value']+" on issue \""+issue_prime['title']+"\" does not exist in the destination repository. Issue added without assignee field.\n\n")
		# 		issue_prime.pop('assignee')
		# 		post_req(url, json.dumps(issue_prime), credentials)


def main():
	parser = argparse.ArgumentParser(description='Migrate Milestones, Labels, and Issues between two GitHub repositories. To migrate a subset of elements (Milestones, Labels, Issues), use the element specific flags (--milestones, --lables, --issues). Providing no flags defaults to all element types being migrated.')
	parser.add_argument('source_repo', type=str, help='the owner and repo to migrate from: <owner>/<repo_name>')
	parser.add_argument('destination_repo', type=str, help='the owner and repo to migrate to: <owner>/<repo_name>')

	parser.add_argument('--repo', '-r', action="store_true", help='Creates new private repository on destination GitHub and clones git commits/branches/tags to the destination. It requires username and token for source and destination.')
	parser.add_argument('--githubData', '-gd', action="store_true", help='Migrates GitHub data (Milestones/Labels/Issues). It requires username and token for source and destination.')
	parser.add_argument('--clone', '-c', action="store_true", help='Clones source repository commits/branchs/tags to the destination. It requires username and token for source and destination unless ssh connection (-s) option.')

	parser.add_argument('--sourceUserName', '-sun', nargs='?', type=str, action='store', dest='sourceUserName', help='Username for source GitHub. Mandatory for create repo (-r), migrade GitHub Data (-gd) options.')	
	parser.add_argument('--sourceToken', '-st', nargs='?', type=str, action='store', dest='sourceToken', help='Your personal access token for the source GitHub account. Mandatory for create repo (-r), migrade GitHub Data (-gd) options.')
	parser.add_argument('--destinationUserName', '-dun', nargs='?', type=str, action='store', dest='destinationUserName', help='Username for destination GitHub. Mandatory for create repo (-r), migrade GitHub Data (-gd) options.')
	parser.add_argument('--destinationToken', '-dt', nargs='?', type=str, action='store', dest='destinationToken', help='Your personal access token for the destination GitHub account. Mandatory for create repo (-r), migrade GitHub Data (-gd) options.')
	parser.add_argument('--ssh', '-s', action="store_true", help='Enable SSH connection for destination github.')

	parser.add_argument('--sourceHost', '-sh', nargs='?', default=ghe_url, type=str, action='store', dest='sourceHost', help='The GitHub host to migrate from. Default is '+ghe_url+'.')
	parser.add_argument('--destinationHost', '-dh', nargs='?', default=github_url, type=str, action='store', dest='destinationHost', help='The GitHub domain to migrate to. Defaults is '+github_url+'.')
	
	parser.add_argument('--inheritVisibility', '-v', action="store_true", help='Inherit visibility (public/private repository) of source repository. By default -r option creates private repository. It works only with -r option.')
	


	args = parser.parse_args()

	destination_repo = args.destination_repo
	source_repo = args.source_repo
	
	if (args.sourceHost == github_url):
		args.sourceHost = github_api_url

	if (args.destinationHost == github_url):
		args.destinationHost = github_api_url

	if (args.sourceHost != github_api_url) and not args.sourceHost.endswith(ghe_api_path):
		args.sourceHost += ghe_api_path

	if (args.destinationHost != github_api_url) and not args.destinationHost.endswith(ghe_api_path):
		args.destinationHost += ghe_api_path

	if not args.repo and not args.clone and not args.githubData:
		sys.stderr.write('GitHub action option is not specified. Either --repo, --clone, --githubData option is required.\n')
		quit()

	if (args.repo or args.githubData) and not (args.sourceUserName and args.sourceToken and args.destinationUserName and args.destinationToken):
		sys.stderr.write('GitHub source and destination user name and token are required.\n')
		quit()

	if args.clone and not args.ssh and not (args.sourceUserName and args.sourceToken and args.destinationUserName and args.destinationToken):
		sys.stderr.write('GitHub source and destination user name and token are required.\n')
		quit()

	source_root = args.sourceHost
	if not source_root.endswith('/'):
		source_root = source_root+'/'

	destination_root = args.destinationHost
	if not destination_root.endswith('/'):
		destination_root = destination_root+'/'

	source_credentials = {'user_name': args.sourceUserName, 'token': args.sourceToken}
	destination_credentials = {'user_name': args.destinationUserName, 'token': args.destinationToken}


	if args.repo:
		repo = download_repository(source_root, source_repo, source_credentials)
		args.clone = True
		args.githubData = True
		if repo:
			res = create_repository(repo, destination_root, destination_repo, destination_credentials, args.inheritVisibility)
		else:
			sys.stderr.write('ERROR: The source repository failed to be retrieved. Exiting...')
			quit()

	if args.clone:
		ssh = args.ssh
		clone = clone_repository(source_root, source_repo, source_credentials, destination_root, destination_repo, destination_credentials, ssh)
		if not clone:
			sys.stderr.write('ERROR: Failed to clone the repository. Exiting...')
			quit()

	if args.githubData:
		milestone_map = None
		milestones = download_milestones(source_root, source_repo, source_credentials)
		if milestones:
			milestone_map = create_milestones(milestones, destination_root, destination_repo, destination_credentials)
		elif milestones == False:
			sys.stderr.write('ERROR: Milestones failed to be retrieved. Exiting...')
			quit()
		else:
			print "No milestones found. None migrated"
		
		labels = download_labels(source_root, source_repo, source_credentials)
		if labels:
			res = create_labels(labels, destination_root, destination_repo, destination_credentials)
		elif labels == False:
			sys.stderr.write('ERROR: Labels failed to be retrieved. Exiting...')
			quit()
		else:
			print "No Labels found. None migrated"
		
		issues = download_issues(source_root, source_repo, source_credentials)
		if issues:
			sameInstall = False
			if (args.sourceHost == args.destinationHost):
				sameInstall = True
			res = create_issues(issues, destination_root, destination_repo, args.milestones, args.labels, milestone_map, destination_credentials, sameInstall)
		elif issues == False:
			sys.stderr.write('ERROR: Issues failed to be retrieved. Exiting...')
			quit()
		else:
			print "No Issues found. None migrated"

if __name__ == "__main__":
	main()
