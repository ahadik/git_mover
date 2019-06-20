# GitMover
A Python script to copy the repository (all commits/branches/labels) and migrate milestones, labels, and issues between repositories.

It cannot migrate pull requests and comments in the pull requests. Pull request is a type of issue github internally, and there is an API to get them.
But a pull request contains github internal data (eg. diff/patch blobs) and there's no API to migrate them.

There was once no easy way to migrate your team's collaborative work (Milestones, Labels, Issues) to another repository. This was especially thorny for teams moving a project into GitHub Enterprise, or open sourcing an existing project by moving it out of GitHub Enterprise. This is a tool to help that process.

## Dependencies
GitMover is just a Python script. You'll need `requests`, and `argparse` installed.
Install them with pip: `pip install requests argparse`.

## Usage
```bash
$ python git-mover.py 
              [-h] 
              [--repo] [--githubData] [--clone]
              [--sourceUserName [SOURCEUSERNAME]] 
              [--sourceToken [SOURCETOKEN]]
              [--destinationUserName [DESTINATIONUSERNAME]]
              [--destinationToken [DESTINATIONTOKEN]]
              [--ssh]
              [--sourceHost [SOURCEHOST]] [--destinationHost [DESTINATIONHOST]]
              [--inheritVisibility]
              source_repo destination_repo
```

### Example
##### Move GHE repository dev/gcp to github.com with milestones, labels, and issues (when repository freshbooks/gcp doesn't exist on target github)
```bash
$ git-mover.py dev/gcp freshbooks/gcp -r --sun <source github username> --st <source github auth token> -dun <destination github username> --dt <desitination github auth token>
```

##### Move GHE repository dev/gcp to github.com with milestones, labels, and issues (when empty repository freshbooks/gcp exist)
```bash
$ git-mover.py dev/gcp freshbooks/gcp -c -gd --sun <source github username> --st <source github auth token> -dun <destination github username> --dt <desitination github auth token>
```

##### Move GHE repository dev/gcp to github.com repository only (commits/branches/tags) when repository freshbooks/gcp exists
```bash
$ git-mover.py dev/gcp freshbooks/gcp -c --sun <source github username> --st <source github auth token> -dun <destination github username> --dt <desitination github auth token>
```

##### Move GHE repository dev/gcp to github.com repository only (commits/branches/tags) with SSH connection when repository freshbooks/gcp exists
```bash
$ git-mover.py dev/gcp freshbooks/gcp -c -s
```

For authentication, GitMover uses a personal access token, which can be generated in your GitHub Profile settings.

### Positional Arguments
  `source_repo`: the team and repo to migrate from: `<team_name>/<repo_name>`
  
  `destination_repo`: the team and repo to migrate to: `<team_name>/<repo_name>`
  
### Optional Arguments

#### GitHub host options (be default source is 2ndsiteinc GitHub Enterprise, destination is github.com)
  `--sourceHost [SOURCE_HOST_URL], -sh [SOURCE_HOST_URL]`: The GitHub domain to migrate from. Defaults to https://github.2ndsiteinc.com.
  
  `--destinationHost [DESTINATION_HOST_URL], -dh [DESTINATION_HOST_URL]`: The GitHub domain to migrate to. Defaults to https://www.github.com. 

#### GitHub Action options

##### Clone the GitHub repository
  `--repo, -r`: Creates new private repository on destination GitHub and clones git commits/branches/tags to the destination. It requires username and token for source and destination. It includes --clone and --githubData options.

##### Copy GitHub data (Milestones/Labels/Issues)
  `--githubData, -gd`: Migrates GitHub data (Milestones/Labels/Issues). It requires username and token for source and destination.

##### Conle the repository to empty GitHub repository (commits/branches/tags)
  `--clone, -c`: Clones source repository commits/branchs/tags to the destination. It requires username and token for source and destination unless ssh connection (-s) option.

#### Credential options
  `--sourceUserName, '-sun`; Username for source GitHub. Mandatory for create repo (-r), migrade GitHub Data (-gd) options.

  `--sourceToken -st`: Your personal access token for the source GitHub account. Mandatory for create repo (-r), migrade GitHub Data (-gd) options.

  `--destinationUserName -dun`: Username for destination GitHub. Mandatory for create repo (-r), migrade GitHub Data (-gd) options.

  `--destinationToken -dt`: Your personal access token for the destination GitHub account. Mandatory for create repo (-r), migrade GitHub Data (-gd) options.

  `--ssh, -s`: Enable SSH connection for destination github. It uses ssh keys for cloning repository. If it is specified with --clone options, source/destination username and password are not required

#### Others
  `--inheritVisibility, -v`: Inherit visibility of source repository. (default is private) It works only with -r option.

  `-h, --help`: show help message and exit.
