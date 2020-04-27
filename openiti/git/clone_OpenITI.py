"""Clone github repositories to your local machine.

Examples:
    Clone all OpenITI 25-year repos::
    
        # >>> repo_list = get_repo_urls(group="orgs", name="OpenITI", 
        #                                path_pattern="\\d{4}AH$")
        # >>> clone_repos(repo_list, r"D:\\OpenITI")

    Clone specific repos::
    
        # >>> base = ""https://github.com/OpenITI/"
        # >>> repo_list = [base+"mARkdown_scheme", base+"RELEASE"]
        # >>> clone_repos(repo_list, r"D:\\OpenITI")

Command line usage:
    To clone all the OpenITI organization's 25-years repos:
    
        ``python clone_OpenITI.py ["orgs" or "users"] [user or org name] [path_pattern] [[dest_folder]]``

        ``dest_folder$ python pth/to/clone_OpenITI.py orgs OpenITI \d+AH$``
    
        ``other_folder$ python pth/to/clone_OpenITI.py orgs OpenITI \d+AH$ path/to/dest_folder``

    If fewer than 3 arguments are given, the program will prompt you for the arguments::

        $ python clone_OpenITI.py
        Enter the organization/user name: openiti
        Organization or User? (orgs/users): orgs
        Enter the regex pattern to match desired repo URLs: \d{4}AH
        Enter the destination folder for the clone: openiti_clone
"""

import sys
import requests
import re
import subprocess


def get_repo_urls(group="orgs", name="OpenITI", path_pattern=r"\d{4}AH$"):
    """Get a list of all repos owned by organisation/user `name`
    that match the regex `path_pattern`

    Args:
        group (str): either "users" or "orgs". Defaults to "orgs"
        name (str): GitHub name of the user/organization. Defaults to "OpenITI"
        path_pattern(str): regex pattern that matches the desired repository names.
            If none is defined, all repos will be cloned. Defaults to r"\d{4}AH$".

    Returns:
        (list): a list of repo urls that matches the `path_pattern` regex.
    """
    repo_urls = []
    page = 1
    while True:
        url = 'https://api.github.com/{0}/{1}/repos?per_page=100&page={2}'
        r = requests.get(url.format(group, name, page))
        print(url.format(group, name, page))
        if r.status_code == 200:
            rdata = r.json()
            for repo in rdata:
                if path_pattern:
                    if re.compile(path_pattern).search(repo['full_name']):
                        repo_urls.append(repo['clone_url'])
                else:
                    repo_urls.append(repo['clone_url'])
            if (len(rdata) >= 100):
                page = page + 1
            else:
                print('Found {0} repos.'.format(len(repo_urls)))
                break
        else:
            print(r)
            return False
    return repo_urls


def clone_repos(all_repos, clone_dir="."):
    """Clone the list of repo urls `all_repos` to the `clone_dir`

    Args:
        all_repos (list): a list of repo urls.
        clone_dir (str): path to the local folder where the repos are to be cloned.
            Defaults to the current active directory.

    Returns:
        None
    """
    print('Cloning...')
    counter = 1
    total_repo_nr = str(len(all_repos))
    for repo in all_repos:
        path_to_clone = clone_dir #+ repo.split("/")[-1]
        print ('\nRepository ' + str(counter) + ' of ' + total_repo_nr + '\n')
        print(path_to_clone)
        p = subprocess.Popen(["git", "clone", repo], cwd=path_to_clone)
        p.wait()
        # os.system('git clone ' + repo + ' ' + path_to_clone + repo.split("/")[-1])
        counter += 1


if __name__ == '__main__':

    # path_pattern = re.compile("\d{4}AH$")
    if len(sys.argv) < 4:
        name = input("Enter the organization/user name: ")
        group = input("Organization or User? (orgs/users): ")
        path_pattern = input("Enter the regex pattern in repo URL: ")
        clone_dir = input("Enter the destination folder for the clone: ")
    else:
        name = sys.argv[1]
        group = sys.argv[2]
        path_pattern = sys.argv[3]
        if sys.argv < 5:
            clone_dir = "."
        else:
            clone_dir = sys.argv[4]

    # print("arg: " ,sys.argv)
    if len(sys.argv) > 0:
        total = get_repo_urls(group, name, path_pattern)
        if total:
            clone_repos(total, clone_dir)
        else:
            print("No repository found!")
    else:
        print('In Terminal, cd to the destination directory in which you want to clone the repos.\n '
              'then run the script:\n'
              '\tpython3 path/to/script/clone_OpenITI.py OpenITI\n'
              'OpenITI is the organization name!')
