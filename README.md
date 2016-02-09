#GitMover
A Python script to migrate milestones, labels, and issues between repositories.

There was once no easy way to migrate your team's collaborative work (Milestones, Labels, Issues) to another repository. This was especially thorny for teams moving a project into GitHub Enterprise, or open sourcing an existing project by moving it out of GitHub Enterprise. This is a tool to help that process.

##Dependencies
GitMover is just a Python script. You'll need `requests`, and `argparse` installed.
Install them with pip: `pip install requests argparse`.

##Usage
`issue_mover.py [-h] [--sourceRoot [SOURCEROOT]] [--destinationRoot [DESTINATIONROOT]] [--milestones] [--labels] [--issues] user_name token source_repo destination_repo`

For authentication, GitMover uses a personal access token, which can be generated in your GitHub Profile settings.

###Positional Arguments
  `user_name`: Your GitHub (public or enterprise) username: name@email.com
  
  `token`: Your GitHub (public or enterprise) private access token
  
  `source_repo`: the team and repo to migrate from: `<team_name>/<repo_name>`
  
  `destination_repo`: the team and repo to migrate to: `<team_name>/<repo_name>`
  
###Optional Arguments
  `-h, --help`: show this help message and exit
  
  `--sourceRoot [SOURCEROOT], -sr [SOURCEROOT]`: The GitHub domain to migrate from. Defaults to https://www.github.com. For GitHub enterprise customers, enter the domain for your GitHub installation.
  
  `--destinationRoot [DESTINATIONROOT], -dr [DESTINATIONROOT]`: The GitHub domain to migrate to. Defaults to https://www.github.com. For GitHub enterprise customers, enter the domain for your GitHub installation.
  
  `--milestones, -m`: Toggle on Milestone migration.
  
  `--labels, -l`: Toggle on Label migration.
  
  `--issues, -i`: Toggle on Issue migration.
