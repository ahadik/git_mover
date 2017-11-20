# GitMover

A Python script to migrate milestones, labels, and issues between repositories.

There was once no easy way to migrate your team's collaborative work (Milestones, Labels, Issues and Projects) to another repository. This was especially thorny for teams moving a project into GitHub Enterprise, or open sourcing an existing project by moving it out of GitHub Enterprise. This is a tool to help that process.

## Dependencies

GitMover is just a Python script. You'll need `requests`, and `argparse` installed.
Install them with pip: `pip install requests argparse`.

## Usage

```
git-mover.py [-h] [--destinationToken [DESTINATIONTOKEN]]
                    [--destinationUserName [DESTINATIONUSERNAME]]
                    [--sourceRoot [SOURCEROOT]]
                    [--destinationRoot [DESTINATIONROOT]] [--milestones]
                    [--labels] [--issues] [--projects] [--forceAssignee]
                    user_name token source_repo destination_repo
```

For authentication, GitMover uses a personal access token, which can be generated in your GitHub Profile settings.

### Positional Arguments

  `user_name`: Your GitHub (public or enterprise) username: name@email.com
  
  `token`: Your GitHub (public or enterprise) personal access token
  
  `source_repo`: the team and repo to migrate from: `<team_name>/<repo_name>`
  
  `destination_repo`: the team and repo to migrate to: `<team_name>/<repo_name>`
  
### Optional Arguments

  `-h, --help`: show this help message and exit
  
  `--sourceRoot [SOURCEROOT], -sr [SOURCEROOT]`: The GitHub domain to migrate from. Defaults to https://api.github.com. For GitHub enterprise customers, enter the domain for your GitHub installation.
  
  `--destinationRoot [DESTINATIONROOT], -dr [DESTINATIONROOT]`: The GitHub domain to migrate to. Defaults to https://api.github.com. For GitHub enterprise customers, enter the domain for your GitHub installation.
  
  `--destinationToken [DESTINATIONTOKEN], -dt [DESTINATIONTOKEN]`: Your personal access token for the destination account, if you are migrating between different GitHub installations.
  
  `--destinationUserName [DESTINATIONUSERNAME], -dun [DESTINATIONUSERNAME]`: Username (email address) for destination account, if you are migrating between different GitHub installations.
  
  `--milestones, -m`: Toggle on Milestone migration, default True.
  
  `--labels, -l`: Toggle on Label migration, default True.
  
  `--issues, -i`: Toggle on Issue migration, default True.

  `--projects, -p`: Toggle on Projects migration, default True.

  `--forceAssignee, -fa`: Force adding assignee even if source and destination hosts are diffrent, default True.

## User mapping

If you are migrating projects between GIT instances (i.e. between github.com and your internal instance of GH Enterprise) is most probably that user names of contributors are diffrent.

To map users between instances please create `users_map.ini` file in root of project (look for `users_map.ini.example`). Left value is source user name - right one is destination user name.

**Please note**

Creators and modifiers will be always set as you, because GH doesn't allow to manipulate this information. For this reason issue/pull_request scripts add to each issue/pull_request body and comment a header with information about source element location and original author of this element.