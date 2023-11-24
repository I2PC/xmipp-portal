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

from .models import Attempt, User, Version, Xmipp
from rest_framework.serializers import ModelSerializer

class UserSerializer(ModelSerializer):
	class Meta:
		model = User
		fields = ['userId', 'country']
class XmippSerializer(ModelSerializer):
	class Meta:
		model = Xmipp
		fields = ['branch', 'updated']

class VersionsSerializer(ModelSerializer):
	class Meta:
		model = Version
		fields = ['os', 'cudaVersion', 'cmakeVersion', 'gccVersion', 'gppVersion', 'sconsVersion']

class AttemptSerializer(ModelSerializer):
	user = UserSerializer()
	xmipp = XmippSerializer()
	version = VersionsSerializer()
	class Meta:
		model = Attempt
		fields = ['user', 'version', 'xmipp', 'date', 'returnCode', 'logTail']

	def validateId(self, value):
		print('Validate')
		# Si el usuario ya existe, no lanzar un error
		#if User.objects.filter(ID=value).exists():
		#    return value
		return value
