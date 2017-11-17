import argparse, sys
import movers

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
    # parser.add_argument('--pull_requests', '-pr', action="store_true", help='Toggle on Pull Requests migration.')
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
    issue_map = None
    same_install = args.sourceRoot == args.destinationRoot or args.forceAssignee

    if not args.milestones and not args.labels and not args.issues and not args.projects: # and args.pull_requests == False:
        args.milestones = True
        args.labels = True
        args.issues = True
        args.projects = True
        # args.pull_requests = True

    if args.projects: # or args.pull_requests == True:
        args.issues = True

    if args.milestones:
        milestones = movers.download_milestones(source_root, source_repo, source_credentials)
        if milestones:
            milestone_map = movers.milestones.create_milestones(milestones, destination_root, destination_repo, destination_credentials)
        elif not milestones:
            sys.stderr.write('ERROR: Milestones failed to be retrieved. Exiting...')
            quit()
        else:
            print "No milestones found. None migrated"

    if args.labels:
        labels = movers.download_labels(source_root, source_repo, source_credentials)
        if labels:
            movers.create_labels(labels, destination_root, destination_repo, destination_credentials)
        elif not labels:
            sys.stderr.write('ERROR: Labels failed to be retrieved. Exiting...')
            quit()
        else:
            print "No Labels found. None migrated"

    if args.issues:
        issues = movers.download_issues(source_root, source_repo, source_credentials)
        
        if issues:
            print "Issues downloaded"
            issue_map = movers.create_issues(issues, destination_root, destination_repo, args.milestones, args.labels, milestone_map, source_credentials, destination_credentials, same_install)
        elif not issues:
            sys.stderr.write('ERROR: Issues failed to be retrieved. Exiting...')
            quit()
        else:
            print "No Issues found. None migrated"
    else:
        issues = False

    if args.projects and issues != False:
        projects = movers.download_projects(source_root, source_repo, source_credentials)
        if projects:
            movers.create_projects(projects, destination_root, destination_repo, issue_map, destination_credentials, {
                "source_url": source_root, 
                "source": source_repo, 
                "credentials": source_credentials,
            })
        elif not projects:
            sys.stderr.write("ERROR: Projects failed to be retrievied. Exiting...")
            quit()
        else:
            print "No Projects found. None migrated"

if __name__ == "__main__":
    main()
