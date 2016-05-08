#!/usr/bin/env python2

# Synchronizes the current player files with a git-repo
import os, sys, time
from git import Repo, GitCommandError, Git

#(naively) construct a path string for a ckey
def get_path(repo_path, name):
	return os.path.normpath(os.path.join(repo_path,"player_saves",name[0],name,"*.sav"))

# Writes a simple .gitignore
def write_gitignore (pd):

	# write .gitignore and commit
	try:
		fs = open(pd, "w")
		fs.write("# Automatically generated\n*.sw*\n!.gitignore\n!*.sav")
		fs.close()
	except Exception as e:
		print "Failed to generate .gitignore, error: "+e

# Create a working repo for the script as defined by path
def create_repo (path, remote, empty=False):
	if not os.path.exists(path):
		raise IOError("No such directory!")

	repo = Repo.init(path, bare=False)
	g = Git(path)
	origin = repo.create_remote('origin', remote)
	g.fetch()
	g.checkout('master')

	# Generate a .gitignore and commit
	if not empty:
		#Write a standard .gitignore
		pd = os.path.join(path,".gitignore")
		write_gitignore(pd)

		try:
			print pd
			repo.git.add(pd, update=True)
			repo.git.commit(m="Initial commit")
			origin.push()
		except Exception as e:
			print "Repo setup failed, error: "+str(e)
			time.sleep(5)


# Update all files
def update_all (path):
	repo = Repo(path)
	repo.git.add("player_saves/*")
	if len(repo.index.diff("HEAD"))>0:
		repo.git.add(update=True)
		repo.git.commit(m="Performed full update at "+str(int(time.time())))

# Update a particular ckey
def update_one (path, ckey):
	repo = Repo(path)
	repo.git.add(get_path(path, ckey))

	try:
		repo.git.commit(m="Updates "+ckey+" for "+str(int(time.time())))
	except GitCommandError as e:
		print "Failed to update, error: "+e
		time.sleep(5)

# Retrieve all saves
def retrieve_all (path):
	remotes = Repo(path).remotes
	if len(remotes)==1:
		remotes[0].pull()
	elif len(remotes)==0:
		print "No remotes!"
	else:
		print "Multiple remotes!"
	

# Retrieves latest saves for ckey
def retrieve_one (path, ckey):
	pass

# Pushes changes to repo
def push_changes (path):
	remotes = Repo(path).remotes
	if len(remotes)==1:
		remotes[0].pull()
		remotes[0].push()
	elif len(remotes)==0:
		print "No remotes!"
	else:
		print "Multiple remotes!"
	

if __name__ == "__main__": #parse shell command from byond or term

	# Missing second arg
	if len(sys.argv)==2:
		print "No repository specified, aborting."

	elif len(sys.argv)==3: #sync.py (action) (repo-path)

		# Update all saves
		if "updall" in sys.argv[1]:
			update_all(sys.argv[2])

		# Retrieve all saves from repo
		elif "retall" in sys.argv[1]:
			retrieve_one(sys.argv[2])
		
		# Push changes
		elif "push" in sys.argv[1]:
			push_changes(sys.argv[2])
		
		else:
			print "Unknown command."

	elif len(sys.argv)==4: #sync.py (action) (repo-path) (arg)
		# Create a working repo for sync
		if "init" in sys.argv[1]:
			print sys.argv[2], sys.argv[3]
			create_repo(sys.argv[2], sys.argv[3])

		# Update specific ckey
		elif "updone" in sys.argv[1]:
			update_one(sys.argv[2], sys.argv[3])

		# Retrieves a specific save
		elif "retone" in sys.argv[1]:
			retrieve_one(sys.argv[2],sys.argv[3])

		else:
			print "Unknown single arg command."
	else:
		print """Usage: sync.py (command) (repo) [args...]
	init (repo) (remote) Initialize the repo.
	updall (repo) Commit all changes to repo.
	updone (repo) (ckey) Update changes for ckey.
	retall (repo) Retrieve all changes from remote.
	retone (repo) (ckey) Retrieve changes for ckey.
	push (repo) Push all changes to remote."""
			

