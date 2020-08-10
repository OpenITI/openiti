from git import Repo
import os


class GitUtil(object):

    def __init__(self, repo: str, user: dict, path: str = ''):
        """ initial method
        To use this class, first make sure you have set ssh private key and give the path
        in the following wapper.
        Save the wrapper as a bash script and give required permissions using "sudo chmod a+x /path/to/ssh_key":

        #!/bin/bash
        ssh -i path/to/ssh/key -oIdentitiesOnly=yes -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null "$@"

        Parameters
        ----------
        repo : str
            The repository ssh url in `git@` format.
        user : dict
            User information: `ssh` wrapper script path, github username and email in the following format, e.g:
            {
                'ssh': '/usr/local/bin/ssh_wrapper',
                'name': 'name',
                'email': 'name@mail.com'
            }
        path : str, optional
            The checkout path.
            If you didn't specify this value, it will based on your current working directory.
            **Make sure that's an empty folder for `git clone`**

            Examples
        --------
        from .utils.git import GitUtils
        git = GitUtils(
            repo='git@github.com:username/repo.git',
            user={
                'ssh': '/usr/local/bin/ssh_wrapper.sh   ',
                'name': 'username',
                'email': 'email@gmail.com',
            }
        )
        # change some file(s) here
        # add, commit, and push files to master
        git.commit('master','commit msg')
        """

        repo = repo.strip()
        path = os.path.join(os.getcwd(), path.strip())
        _ = {'ssh': '', 'name': 'name', 'email': 'name@gmail.com'}
        _.update(user)
        user = _

        if not repo.startswith('git@'):
            raise Exception(
                f'Invalid checkout url: {repo}\n\n'
                'Please use the valid ssh url with the following format:\n'
                ' `git@github.com:account/repository.git` format\n\n'
            )

        if not os.path.isfile(user['ssh']):
            raise Exception(
                f'Missing custom ssh wrapper {user["ssh"]}!\n\n'
                'Please provide a custom shh wrapper script with the correct ssh private key.\n'
                'The bash script should contain this line:\n\n'
                'ssh -i <path_to_ssh_private_key> -oIdentitiesOnly=yes -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null "$@"\n\n'
            )

        os.environ['GIT_SSH'] = user['ssh']
        if os.path.isdir(path):
            self.repo = Repo(path)
            self.repo.git.pull('origin', 'master')
        else:
            os.makedirs(path)
            self.repo = Repo.clone_from(repo, path, env={'GIT_SSH': user['ssh']})
            self.repo.config_writer().set_value('user', 'name', user['name']).release()
            self.repo.config_writer().set_value('user', 'email', user['email']).release()

    def commit(self, branch: str = 'master', message: str = 'Auto commit'):
        """Commit method.
        This method will add, commit, and push all changes including untracked file.

        Parameters
        ----------
        branch : str, optional
            The branch you would like to commit. Default is master
        message : str, optionl
            Commit message
        """
        has_changed = False

        # Check if there's any untracked files
        for file in self.repo.untracked_files:
            print(f'Added untracked file: {file}')
            self.repo.git.add(file)
            if has_changed is False:
                has_changed = True

        if self.repo.is_dirty() is True: # reacts like git status
            for file in self.repo.git.diff(None, name_only=True).split('\n'):
                print(f'Added file: {file}')
                self.repo.git.add(file)
                if has_changed is False:
                    has_changed = True

        if has_changed is True:
            self.repo.git.commit('-m', message)
            self.repo.git.push('origin', branch)
