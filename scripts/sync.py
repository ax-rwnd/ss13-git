
# Synchronizes the current player files with a git-repo
import os, sys, time
from git import Repo, GitCommandError, Git

#(naively) construct a path string for a ckey
def get_path(repo_path, name):
	return os.path.normpath(os.path.join(repo_path,"player_saves",name[0],name,"*.sav"))

def set_defaults (repo):
	cw = repo.config_writer()
	cw.set_value("push", "default", "current")
	cw.set_value("pull", "default", "current")
	cw.release()

# Create a working repo for the script as defined by path
def create_repo (path, remote, ignore=False, existing=True, push=True):
	if not os.path.exists(path):
		raise IOError("No such directory!")

	repo = Repo.init(path, bare=False)

	# Generate a .gitignore
	pd = os.path.join(path,".gitignore")
	if ignore:
		fs = open(pd, "w")
		fs.write("# Automatically generated\n*.sw*\n!.gitignore\n!*.sav")
		fs.close()
	else:
		#Write empty gitignore (gitpython limitation?)
		fs = open(pd, "w")
		fs.write("\0")
		fs.close()

	#Commit .gitignore
	repo.git.add(pd)
	repo.git.commit(m="Initial commit.")

	#Set defaults
	set_defaults(repo)

	#Add origin remote
	origin = repo.create_remote('origin', remote)
	origin.fetch()
	assert origin.exists()
	assert origin == repo.remotes.origin == repo.remotes['origin']

	#Create master branch
	repo.create_head('master')

	#Commit existing files
	if existing and len(repo.untracked_files)>0:
		repo.git.add("player_saves/*")
		repo.git.commit(m="Added existing savefiles")

	#Push to remote
	if push:
		origin.push()

# Clone into an existing repo
def clone_repo (path, remote):

	# Clone into repo
	repo = Repo.clone_from(remote, path)
	assert repo is not Repo

	# Write config defaults
	set_defaults(repo)
	

# Update all files
def update_all (path):
	repo = Repo(path, search_parent_directories=True)
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
			create_repo(sys.argv[2], sys.argv[3], True)

		# Clone into an existing repo
		elif "clone" in sys.argv[1]:
			clone_repo(sys.argv[2], sys.argv[3])

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
	clone (repo) (remote) Clone into an existing repo.
	updall (repo) Commit all changes to repo.
	updone (repo) (ckey) Update changes for ckey.
	retall (repo) Retrieve all changes from remote.
	retone (repo) (ckey) Retrieve changes for ckey.
	push (repo) Push all changes to remote."""
			

