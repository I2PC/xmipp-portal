#!/usr/bin/env python3
# ***************************************************************************
# * Authors:		Alberto García (alberto.garcia@cnb.csic.es)
# *							Martín Salinas (martin.salinas@cnb.csic.es)
# *             Carolina Simón (carolina.simon@cnb.csic.es)
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307 USA
# *
# * All comments concerning this program package may be sent to the
# * e-mail address 'scipion@cnb.csic.es'
# ***************************************************************************/

from __future__ import unicode_literals
from django.db import models

class User(models.Model):
    userId = models.CharField(max_length=100, primary_key=False)
    country = models.CharField(max_length=100)

class Version(models.Model):
    os = models.CharField(max_length=100) # cat /etc/os-release
    cudaVersion = models.CharField(max_length=20)
    cmakeVersion = models.CharField(max_length=20)
    gccVersion = models.CharField(max_length=20)
    gppVersion = models.CharField(max_length=20)
    sconsVersion = models.CharField(max_length=20, default='')

class Xmipp(models.Model):
    branch = models.CharField(max_length=50) #XMIPP_VERNAME
    updated = models.BooleanField() #git fecth + git status

class Attempt(models.Model):
    user = models.ForeignKey(User, related_name='attemps', on_delete=models.CASCADE)
    version = models.ForeignKey(Version, on_delete=models.CASCADE)
    xmipp = models.ForeignKey(Xmipp, on_delete=models.CASCADE)

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