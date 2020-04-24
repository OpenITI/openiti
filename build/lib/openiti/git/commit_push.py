"""Scripts to commit and push GitHub repos.

In development. Pushing does not work yet.

The problem is how to use GitHub authentication.

"""

import subprocess
import os

def run_command(command, cwd, verbose=True):
    """Run a command line command and print the output.

    Args:
        command (list): a list containing the elements of the command,
                        e.g., ["git", "commit", "-m", msg]
        cwd (str): path to folder where command needs to be carried out
        verbose (bool): if verbose is set to True, output is printed

    See https://www.endpoint.com/blog/2015/01/28/getting-realtime-output-using-python
    """
    process = subprocess.Popen(command, cwd=cwd,
                               stdout=subprocess.PIPE)
    print("process started")
    while True:
        output = process.stdout.readline()
        if process.poll() is not None:
            print(process.poll())
            break
        if verbose:
            if output:
                print(output.strip())
    print("finished")
    rc = process.poll()
    return rc

def run_command(command, cwd, verbose=True):
    """Run a command line command and print the output.

    Args:
        command (list): a list containing the elements of the command,
                        e.g., ["git", "commit", "-m", msg]
        cwd (str): path to folder where command needs to be carried out
        verbose (bool): if verbose is set to True, output is printed
    """
    output = subprocess.check_output(command, cwd=cwd)
    if verbose:
        print(output.decode().strip())
    return output.decode().strip()


def get_commit_msg(msg=None):
    """Define a message for the commit.

    Args:
        msg (str): user-defined message. If no msg is provided,
            the user will be given the choice between
            a default commit message and a user-defined message.
    """
    if msg:
        return msg
    else:
        default_msg = "Updated repo"
        print("Use default commit message?")
        print("    '{}'".format(default_msg))
        resp = input("Y/N: ")
        if resp.upper() == "N":
            msg = input("Write commit message: ")
        else:
            msg = default_msg
        return msg

    
def is_git_repo(pth="."):
    """Check whether the folder at pth is a git repo.

    See https://stackoverflow.com/a/24584384

    Returns:
        bool: True if pth is a git repo, False if it isn't.
    """
    return subprocess.call(["git", "-C", pth, 'status'],
                           stderr=subprocess.STDOUT,
                           stdout = open(os.devnull, 'w')) == 0
    

def commit_repo(repo_pth, add=["."], msg=None):
    """Add changed files and commit.

    Args:
        repo_pth (str): path to the repository to be committed
        add (list): a list of file patterns to be added for commit
        msg (str): a commit message. If None, user will be asked
            whether a default message should be used,
            or else to provide one.
    """
    if not msg:
        msg = get_commit_msg(msg)
    if is_git_repo(repo_pth):
        for it in add:
            print("GIT ADD", it)
            run_command(["git", "add", it], cwd=repo_pth)
##            p = subprocess.Popen(["git", "add", it],
##                                 cwd=repo_pth)
##            p.wait()
        print("GIT COMMIT -M '{}'".format(msg))
        run_command(["git", "commit", "-m", msg], cwd=repo_pth)
##        p = subprocess.Popen(["git", "commit", "-m", msg],
##                             cwd=repo_pth)
        print("Repo {} committed successfully".format(repo_pth))
    else:
        print("Aborted: folder {} is not a git repo".format(repo_pth))

def commit_all_repos_in_folder(folder, add=["."], msg=None):
    """Commit changes in all repos in a folder.

    Args:
        folder (str): path to the folder containing the repos
        add (list): a list of file patterns to be added for commit
        msg (str): a commit message. If None, user will be asked
            whether a default message should be used,
            or else to provide one.
    """
    if not msg:
        msg = get_commit_msg(msg)
    for repo in os.listdir(folder):
        repo_pth = os.path.join(folder, repo)
        commit_repo(repo_pth, add, msg)

def get_remote_url(repo_pth):
    """Get the remote url of a repo."""
    if is_git_repo(repo_pth):
        print("GIT CONFIG --GET REMOTE.ORIGIN.URL")
        return run_command(["git", "config", "--get", "remote.origin.url"],
                           cwd=repo_pth)
    else:
        print("Aborted: folder {} is not a git repo".format(repo))

def push(repo_pth, branch="master"):
    """Push a repo to the remote.
    THIS FUNCTION DOES NOT WORK !!!!!"""
    if is_git_repo(repo_pth):
        try:
            print("GIT PUSH -U ORIGIN", branch)
            run_command(["git", "push", "-u", "origin", branch], cwd=repo_pth)
        except:
            print("failed")
            try:
                remote = get_remote_url(repo_pth)
            except:
                print(repo_pth, ": no remote defined!")
                return
            print("GIT PUSH", remote, branch)
            run_command(["git", "push", "-u", remote, branch], cwd=repo_pth)
            print("Repo {} pushed to remote".format(repo))
    else:
        print("Aborted: folder {} is not a git repo".format(repo))
            
def push_all_repos_in_folder(folder, origin="origin", branch="master"):
    """Push all repos in a folder to the remote."""
    for repo in os.listdir(folder):
        repo_pth = os.path.join(folder, repo)
        push(repo_pth, origin="origin", branch="master")

            
def add_origin(repo_pth, user, token, remote_url, origin="origin"):
    """Add a remote origin to a repo.

    Args:
        repo_pth (str): path to the repo
        user (str): user name of the user
        token (str): GitHub access token;
            if None, user will be prompted to provide it.
        remote_url (str): url of the remote git
        origin (str): name of the remote.

    See https://stackoverflow.com/questions/18935539/authenticate-with-github-using-a-token
    """
    if token == None:
        token = input("GitHub access token: ")
    #r = remote_url.replace("//", "//{}:{}@".format(user, token))
    r = remote_url.replace("//", "//{}@".format(token))
    try:
        print("GIT REMOTE SET-URL", origin, r)
        run_command(["git", "remote", "set-url", origin, r],
                    cwd=repo_pth)
    except:
        print("failed; try:")
        print("GIT REMOTE ADD", origin, r)
        run_command(["git", "remote", "add", origin, r],
                    cwd=repo_pth)

    
if __name__ == "__main__":

    token_fp = r"D:\London\OpenITI\python_library\test_git_repo\GitHub personalAccessTokenReadOnly.txt"
    try:
        with open(token_fp,
                  mode="r", encoding="utf-8") as file:
            token = file.read().strip()
    except:
        token = None # you will be prompted to insert the token manually
    print("token:", token)

    folder = r"D:\London\OpenITI\python_library\test_git_repo"
    print(is_git_repo(folder))


    remote_url = "https://github.com/pverkind/test_git_repo.git"
    add_origin(folder, "pverkind", token, remote_url)



    commit_repo(folder, add=["README.md", ".gitignore"],
                msg="Automatic commit")
    run_command(["git", "status"], cwd=folder)

    remote = run_command(["git", "config", "--get", "remote.origin.url"],
                         cwd=folder)
    print(remote)

    push(folder, branch="master")
    ##msg = "Updated yml files during automatic metadata creation."
    ##commit_all_repos_in_folder(folder, msg)
