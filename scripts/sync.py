#!/usr/bin/env python2

# Synchronizes the current player files with a git-repo
import os, sys, time
from git import Repo, GitCommandError

#(naively) construct a path string for a ckey
def get_path(repo_path, name):
	return os.path.normpath(os.path.join(repo_path,"player_saves",name[0],name,"*.sav"))

# Writes a simple .gitignore
def write_gitignore (path):
	#Write a standard .gitignore
	pd = os.path.join(path,".gitignore")

	# write .gitignore and commit
	try:
		fs = open(pd, "w")
		fs.write("# Automatically generated\n# sync.py init will replace this by default\n*.sw*\n!.gitignore\n!*.sav")
		fs.close()
	except Exception as e:
		print "Failed to generate .gitignore, error: "+e

# Create a working repo for the script as defined by path
def create_repo (path, genignore=True):
	repo = Repo.init(path, bare=False)

	#generate a .gitignore
	if genignore:
		write_gitignore(path)

	if len(repo.index.diff("HEAD"))>0:
		repo.git.add(pd) #TODO confirm functionality...

		try:
			repo.git.commit(m="Initial commit")
		except Exception as e:
			print "Repo setup failed, error: "+e
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

def retrieve_all (path):
	pass

def retrieve_one (path, ckey):
	pass
	

if __name__ == "__main__": #parse shell command from byond

	if len(sys.argv)==3: #sync.py (action) (repo-path)

		# Create a working repo for sync
		if "init" in sys.argv[1]:
			create_repo(sys.argv[2])

		# Update all saves
		elif "updall" in sys.argv[1]:
			update_all(sys.argv[2])

		# Retrieve all saves from repo
		elif "retall" in sys.argv[1]:
			retrieve_one(sys.argv[2])

	elif len(sys.argv)==4: #sync.py (action) (repo-path) (ckey)

		# Update specific ckey
		if "updone" in sys.argv[1]:
			update_one(sys.argv[2], sys.argv[3])

		# Retrieves a specific save
		elif "retone" in sys.argv[1]:
			retrieve_one(sys.argv[2],sys.argv[3])
