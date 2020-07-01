#!/usr/bin/python3

import os
from subprocess import Popen, PIPE


EXCLUDE = set([
    'master',
    'dev',
    'development',
])

WHITE = '\033[1;37;40m' 
RED = "\033[1;31;40m"
GREEN = "\033[1;32;40m"


def read_branches():
    proc = Popen(
        'git branch -l',
        shell=True,
        stdout=PIPE,
        stderr=PIPE
    )
    proc.wait()
    branches, stderr = proc.communicate()
    if proc.returncode:
        print(stderr)
        exit(0)
    return branches.decode()


def remove_branch(branch):
    os.system(f'git branch -D {branch}')


if __name__ == '__main__':
    branches = set(map(lambda x: x.strip(), read_branches().replace('* ', '').splitlines()))
    will_safe = branches & EXCLUDE
    will_remove = branches - EXCLUDE
    
    print(f'{WHITE}Branches will be safe:')
    list(map(lambda x: print(f'{GREEN}{x}'), will_safe))
    print(f'{WHITE}Branches will be remove:')
    list(map(lambda x: print(f'{RED}{x}'), will_remove))
    print(f'{WHITE}Confirm? [y/n]')
    action = input()
    if action.lower() != 'y':
        exit(0)

    for branch in will_remove:
        print(branch, end='\t')
        #remove_branch()
        print('[OK]')
