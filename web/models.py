from __future__ import unicode_literals
from django.db import models

class User(models.Model):
    ID = models.CharField(max_length=100, primary_key=True)
    country = models.CharField(max_length=100)

class Machine(models.Model):
    os = models.CharField(max_length=100) # cat /etc/os-release
    cudaVersion = models.CharField(max_length=20)
    cmakeVersion = models.CharField(max_length=20)
    gccVersion = models.CharField(max_length=20)
    gppVersion = models.CharField(max_length=20)

class Xmipp(models.Model):
    branch = models.CharField(max_length=50) #XMIPP_VERNAME
    updated = models.BooleanField() #git fecth + git status

class Attempt(models.Model):
    user = models.ForeignKey(User, related_name='attemps', on_delete=models.CASCADE)
    machine = models.ForeignKey(Machine, related_name='machines', on_delete=models.CASCADE)
    xmipp = models.ForeignKey(Xmipp, related_name='xmipps', on_delete=models.CASCADE)

    date = models.DateTimeField(auto_now_add=True)
    returnCode = models.CharField(max_length=300)
    logTail = models.TextField(max_length=10000)

'''#to get the updated status
#!/bin/bash

# Update all remote tracking branches
git fetch

# Get the latest commit hashes of the local and remote branches
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})

# Compare the commit hashes
if [ $LOCAL = $REMOTE ]; then
    echo 0
else
    echo 1
fi
'''