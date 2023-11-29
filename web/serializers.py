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

# General imports
from rest_framework.serializers import ModelSerializer

# Self imports
from .models import Attempt, User, Version, Xmipp
from .constants import USER_ID, USER_COUNTRY, XMIPP_BRANCH, XMIPP_UPDATED, VERSION_OS, VERSION_CUDA,\
	VERSION_CMAKE, VERSION_GCC, VERSION_GPP, VERSION_SCONS, ATTEMPT_USER, ATTEMPT_VERSION, ATTEMPT_XMIPP,\
	ATTEMPT_DATE, ATTEMPT_RETCODE, ATTEMPT_LOGTAIL, VERSION_ARCHITECTURE

class UserSerializer(ModelSerializer):
	class Meta:
		model = User
		fields = [USER_ID, USER_COUNTRY]
class XmippSerializer(ModelSerializer):
	class Meta:
		model = Xmipp
		fields = [XMIPP_BRANCH, XMIPP_UPDATED]

class VersionsSerializer(ModelSerializer):
	class Meta:
		model = Version
		fields = [VERSION_OS, VERSION_ARCHITECTURE, VERSION_CUDA, VERSION_CMAKE, VERSION_GCC, VERSION_GPP, VERSION_SCONS]

class AttemptSerializer(ModelSerializer):
	user = UserSerializer()
	xmipp = XmippSerializer()
	version = VersionsSerializer()
	class Meta:
		model = Attempt
		fields = [ATTEMPT_USER, ATTEMPT_VERSION, ATTEMPT_XMIPP, ATTEMPT_DATE, ATTEMPT_RETCODE, ATTEMPT_LOGTAIL]
