# git-ss13 - A git-based synchronization script for Space Station 13

## Goals
To create a...
* continuous backup utility for SS13 servers.
* model for distributing characters between servers.
* simple way of keeping your players' saves backed up.

## Requirements
* Python 2
* Git
* GitPython 2.0.2

## Project status
This is currently a work-in-progress and features may be added and deleted at any time. Some features mentioned in this readme might not even exist yet, YMMV.

## Usage
The current way of using git-ss13 generally follows the pattern:
* Clone the repo into your distribution's root directory (making a separate .git for it is probably advisable).
* Add configuration strings to your distribution and configuration files.
* Hook your player save/load mechanisms to update_one/retrieve_one using previously mentioned configuration and scripts/sync.py.
* Hook a timed event and/or roundend to push changes.
* Configure a git repo under data/ using "sync.py init SS13_PATH/data REMOTE_PATH".
