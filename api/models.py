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
	country = models.CharField(max_length=100, null=True, blank=True)

	def __str__(self):
		return '%s (%s)' % (self.userId, self.country)

class Version(models.Model):
	os = models.CharField(max_length=100, null=True, blank=True) # cat /etc/os-release
	cuda = models.CharField(max_length=20, null=True, blank=True)
	cmake = models.CharField(max_length=20, null=True, blank=True)
	gcc = models.CharField(max_length=20, null=True, blank=True)
	gpp = models.CharField(max_length=20, null=True, blank=True)
	scons = models.CharField(max_length=20, default='', null=True, blank=True) #TODO quitar
	architecture = models.CharField(max_length=40, default='', null=True, blank=True)

class Xmipp(models.Model):
	branch = models.CharField(max_length=50) #XMIPP_VERNAME
	updated = models.BooleanField(null=True, blank=True) #git fecth + git status

	def __str__(self):
		return '%s (%s)' % (self.branch, self.updated)

class Attempt(models.Model):
	user = models.ForeignKey(User, related_name='attempts', on_delete=models.CASCADE)
	version = models.ForeignKey(Version, on_delete=models.CASCADE)
	xmipp = models.ForeignKey(Xmipp, on_delete=models.CASCADE)

	date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
	returnCode = models.IntegerField()
	logTail = models.CharField(max_length=10000, default='', null=True, blank=True)

	def __str__(self):
		return '%s - %s (%s)' % (self.user, self.returnCode, self.date)
	
	