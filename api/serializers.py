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
from rest_framework.serializers import ModelSerializer, CharField

# Self imports
from .models import Attempt, User, Version, Xmipp
from .constants import USER_ID, USER_COUNTRY, XMIPP_BRANCH, XMIPP_UPDATED, VERSION_OS, VERSION_CUDA,\
	VERSION_CMAKE, VERSION_GCC, VERSION_GPP, ATTEMPT_USER, ATTEMPT_VERSION, ATTEMPT_XMIPP,\
	ATTEMPT_DATE, ATTEMPT_RETCODE, VERSION_ARCHITECTURE, ATTEMPT_LOGTAIL, VERSION_MPI, VERSION_PYTHON,\
	VERSION_SQLITE, VERSION_JAVA, VERSION_HDF5, VERSION_JPEG

class UserSerializer(ModelSerializer):
	class Meta:
		model = User
		fields = [USER_ID, USER_COUNTRY]
	
	country = CharField(allow_null=True, required=False)
class XmippSerializer(ModelSerializer):
	class Meta:
		model = Xmipp
		fields = [XMIPP_BRANCH, XMIPP_UPDATED]
	
	updated = CharField(allow_null=True, required=False)

class VersionsSerializer(ModelSerializer):
	class Meta:
		model = Version
		fields = [VERSION_OS, VERSION_ARCHITECTURE, VERSION_CUDA, VERSION_CMAKE, \
			VERSION_GCC, VERSION_GPP, VERSION_MPI, VERSION_PYTHON, VERSION_SQLITE, \
			VERSION_JAVA, VERSION_HDF5, VERSION_JPEG]

	os = CharField(allow_null=True, required=False)
	cuda = CharField(allow_null=True, required=False)
	cmake = CharField(allow_null=True, required=False)
	gcc = CharField(allow_null=True, required=False)
	gpp = CharField(allow_null=True, required=False)
	architecture = CharField(allow_null=True, required=False)
	mpi = CharField(allow_null=True, required=False)
	python = CharField(allow_null=True, required=False)
	sqlite = CharField(allow_null=True, required=False)
	java = CharField(allow_null=True, required=False)
	hdf5 = CharField(allow_null=True, required=False)
	jpeg = CharField(allow_null=True, required=False)

class AttemptSerializer(ModelSerializer):
	user = UserSerializer()
	xmipp = XmippSerializer()
	version = VersionsSerializer()
	class Meta:
		model = Attempt
		fields = [ATTEMPT_USER, ATTEMPT_VERSION, ATTEMPT_XMIPP, ATTEMPT_DATE, ATTEMPT_RETCODE, ATTEMPT_LOGTAIL]

	logTail = CharField(allow_null=True, required=False)
	date = CharField(allow_null=True, required=False)