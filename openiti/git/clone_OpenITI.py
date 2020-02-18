import sys
import requests
import re
import subprocess


def get_total_repos(group, name, path_pattern):
    repo_urls = []
    page = 1
    while True:
        url = 'https://api.github.com/{0}/{1}/repos?per_page=100&page={2}'
        r = requests.get(url.format(group, name, page))
        print(url.format(group, name, page))
        if r.status_code == 200:
            rdata = r.json()
            for repo in rdata:
                if re.compile(path_pattern).search(repo['full_name']):
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


def clone_repos(all_repos, clone_dir):
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
    type = input("Organization or User (orgs/users)?: ")
    org_name = input("Enter the organization name: ")
    path_pattern = input("Enter the regex pattern in repo URL: ")
    clone_dir = input("Enter the path to clone: ")
    # print("arg: " ,sys.argv)
    if len(sys.argv) > 0:
        total = get_total_repos(type, org_name, path_pattern)
        # for clone_OpenITI.py orgs OpenITI usage. Then, len(sys.argv) have to be >2!
        # total = get_total_repos(sys.argv[1], sys.argv[2])
        if total:
            clone_repos(total, clone_dir)
        else:
            print("No repository found!")
    else:
        print('In Terminal, cd to the destination directory in which you want to clone the repos.\n '
              'then run the script:\n'
              '\tpython3 path/to/script/clone_OpenITI.py OpenITI\n'
              'OpenITI is the organization name!')