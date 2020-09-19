#!/usr/bin/env python
# coding: utf-8

# 
# 

# # Check Python Version

# In[45]:


import sys
print(sys.executable)
print(sys.version)
print(sys.version_info)


# # Load libraries

# In[2]:


import numpy as np
import pandas as pd
import os

# Specify git executable file for GitPython in Jupyter Notebook (In IDE, it can still work without this line.)
os.environ["GIT_PYTHON_GIT_EXECUTABLE"] = "C:\Program Files\Git\cmd\git.exe"

import git
from git import RemoteProgress

from git import Repo
import matplotlib.pyplot as plt
import seaborn as sns

class Progress(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        print(self._cur_line)



remote_link = "https://github.com/jenkinsci/jenkins"
local_link = "repo/jenkins"
# Uncomment to clone
Repo.clone_from(remote_link, local_link, progress=Progress())


repo = Repo(local_link)
fixing_commit = "ccc374a7176d7704941fb494589790b7673efe2e"
affected_file = "core/src/main/java/jenkins/model/Jenkins.java"


show_data = repo.git.show("-s", fixing_commit).splitlines()
print("Fixing Commit:")
for line in show_data:
    print(line)


diff_data = repo.git.diff("--unified=0", fixing_commit + "^", fixing_commit).splitlines()
actual_line = -1
line_string = ""
for line in diff_data:
    # print(line)
    if(line.find("@@ -") != -1):
        line_string = line[4: line.find(" +")]

print("Line with vulnerabiltiy fix is: " + line_string)


blame_data = repo.git.blame("-L"+line_string+",+1","-wC",fixing_commit + "^", "--", affected_file).splitlines()
vulnerable_commit = ""
for line in blame_data:
    # print(line)
    vulnerable_commit = line[0: line.find(" ")]

print("The vulnerablility contributing commit was: "+vulnerable_commit)

show_data = repo.git.show(vulnerable_commit).splitlines()
for line in show_data:
    print(line)


file_data = repo.git.show("--format=","--stat","--dirstat",vulnerable_commit).splitlines()
insertions = -1
deletions = -1
print("Affected files and directories:")
for line in file_data:
    print(line)
    placeholder_line = line.find("files changed, ")
    if(placeholder_line != -1):
        insertions = line[int(placeholder_line)+15: line.find(" insertions(+)")]
        deletions = line[line.find(" insertions(+), ")+16: line.find(" deletions(-)")]

print("Insertions: " + insertions)
print("Deletions: " + deletions)


# Re for regualr expression searching
import re
comment_additions = 0
comment_deletions = 0
blankline_additions = 0
blankline_deletions = 0
for line in show_data:
    if re.search('^[+]\s*[*]', line) or re.search('^[+]\s*[\/][*]', line) or re.search('^[+]\s*[\/][\/]', line):
        comment_additions = comment_additions + 1
    elif re.search('^[-]\s*[*]', line) or re.search('^[-]\s*[\/][*]', line) or re.search('^[-]\s*[\/][\/]', line):
        comment_deletions = comment_deletions + 1
    elif re.search('^[+]\s*$', line):
        blankline_additions = blankline_additions + 1
    elif re.search('^[-]\s*$', line):
        blankline_deletions = blankline_deletions + 1

# print("Comment additions: " + str(comment_additions))
# print("Comment deletions: " + str(comment_deletions))
# print("Blank line additions: " + str(blankline_additions))
# print("Blank line deletions: " + str(blankline_deletions))
# print("Total Ignored additions: " + str(blankline_additions + comment_additions))
# print("Total Ignored deletions: " + str(blankline_deletions + comment_deletions))
print("Total lines added excluding comments and blank lines: " + str(int(insertions) - (blankline_additions + comment_additions)))
print("Total lines deleted excluding comments and blank lines: " + str(int(deletions) - (blankline_deletions + comment_deletions)))


import datetime

show_files_only = repo.git.show("--format=","--name-only",vulnerable_commit).splitlines()
# Time of this commit and convert
this_commit = repo.git.log("-1","--format=%ci",vulnerable_commit)
this_commit = datetime.datetime.strptime(this_commit,'%Y-%m-%d %H:%M:%S %z')
# print(this_commit)
for line in show_files_only:
    last_commit = 0
    # Get time of last commit, exception means the commit doesn't exist which means it came from the VCC
    try:
        last_commit = repo.git.log("-1","--skip","1","--format=%ci",vulnerable_commit,"--",line)
        last_commit = datetime.datetime.strptime(last_commit,'%Y-%m-%d %H:%M:%S %z')
    except Exception as e:
        # print(str(e))
        last_commit = this_commit
    total_commits = repo.git.log("--name-only","--format=",vulnerable_commit,"--",line).splitlines()
    total_commit_num = 0
    for commits in total_commits:
        if re.search(line,commits):
            total_commit_num = total_commit_num + 1
    print(line + " - " + str((this_commit - last_commit)) + " - Total Commits: " + str(total_commit_num))

print("Developers by file:")
developer_dict = {}

for line in show_files_only:
    print(line)
    developers = repo.git.shortlog("--summary",vulnerable_commit,"--",line).splitlines()
    for developer in developers:
        print(developer)
        # Get the number of commits and developer name and add them to the dictionary
        test = re.search("^\s+\d",developer)
        test2 = re.search("\s+[a-zA-Z]",developer)
        test3 = re.search("[a-zA-Z]+$",developer)
        if(test != None):
            commits = developer[test.end()-1 : test2.start()]
            dev = developer[test3.start() : test3.end()]
            if(dev in developer_dict):
                developer_dict[dev] = int(developer_dict[dev]) + int(commits)
            else:
                developer_dict[dev] = int(commits)

print("Developers by commits on affected files:")
for x, y in developer_dict.items():
  print(x, y)
