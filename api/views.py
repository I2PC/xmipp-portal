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
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status

# Self imports
from .models import User, Xmipp, Version, Attempt
from .serializers import AttemptSerializer
from .utils import getClientIp, getCountryFromIp
from .constants import USER_ID, USER_COUNTRY, XMIPP_BRANCH, XMIPP_UPDATED, VERSION_OS, VERSION_CUDA,\
	VERSION_CMAKE, VERSION_GCC, VERSION_GPP, VERSION_SCONS, ATTEMPT_USER, ATTEMPT_VERSION, ATTEMPT_XMIPP,\
	ATTEMPT_RETCODE, ATTEMPT_LOGTAIL, VERSION_ARCHITECTURE

class AttemptsView(APIView):
  """
	### This class performs a custom processing of the requests received.
	"""
  serializer_class = AttemptSerializer

  def get(self, request, format: str=None) -> JsonResponse:
    """
    ### This function receives a GET request and returns all attempts's info.

    #### Params:
    - request (Any): Django request.
    - format (str): Optional. Request format.

    #### Returns:
    (JsonResponse): JSON with attempts's info.
    """
    # Create a list with all the attempts in database
    attempts = [attempt.user for attempt in Attempt.objects.all()]

    # Return attempts as JSON
    return JsonResponse({'Attempt': attempts})
    #return Response({'data': AttemptSerializer(attempt).data})

  def post(self, request, format: str='json') -> Response:
    """
    ### This function receives a POST request and stores the received data in the database.

    #### Params:
    - request (Any): Django request.
    - format (str): Optional. Request format.

    #### Returns:
    (Response): Http response with the appropiate info.
    """
    # Get data from serializer
    serializer = self.serializer_class(data=request.data)

    # We only want to store valid requests, meaning serializer has to
    # validate and format has to be json (the only one we accept)
    if serializer.is_valid() and format == 'json':
      # Get serializer data into variables
      validatedData = serializer.validated_data
      userData = validatedData.get(ATTEMPT_USER)
      versionData = validatedData.get(ATTEMPT_VERSION)
      xmippData = validatedData.get(ATTEMPT_XMIPP)
      returnCode = validatedData.get(ATTEMPT_RETCODE)
      logTail = validatedData.get(ATTEMPT_LOGTAIL)

      # Obtaining country from sender's ip
      country = getCountryFromIp(getClientIp(request))

      # Creating user object
      userObj = User.objects.update_or_create(
        userId=userData[USER_ID],
        defaults={USER_COUNTRY: country}
      )[0]

      # Creating xmipp object
      xmippObj = Xmipp.objects.get_or_create(
        branch=xmippData[XMIPP_BRANCH],
        updated=xmippData[XMIPP_UPDATED]
      )[0]

      # Creating version object
      versionsObj = Version.objects.get_or_create(
        os=versionData[VERSION_OS],
        architecture=versionData[VERSION_ARCHITECTURE],
        cuda=versionData[VERSION_CUDA],
        cmake=versionData[VERSION_CMAKE],
        gcc=versionData[VERSION_GCC],
        gpp=versionData[VERSION_GPP],
        scons=versionData[VERSION_SCONS]
      )[0]

      # Creating installation attempt object
      attempt = Attempt(user=userObj,
        version=versionsObj,
        xmipp=xmippObj,
        #date=date,
        returnCode=returnCode,
        logTail=logTail
      )

      # Saving attempt
      attempt.save()

      # Return a response contaning the attempt data
      return Response({'data': AttemptSerializer(attempt).data})
    else:
      # In case received data does not validate, return a response with some info
      print('ERRORS: {}\n'.format(serializer.errors))
      return Response(
        {
          'Holi ': 0,
          'isValid': serializer.is_valid(),
          'isJSON': format == 'json'
        },
        status=status.HTTP_400_BAD_REQUEST
      )

'''
curl --header "Content-Type: application/json" -X POST --data '{
        "user": {
        "userId": "hashMachine5", "country": ""
        },
        "version": {
        "os": "Centor",
        "architecture": "skylaque",
        "cuda": "NoSequeeseso",
        "cmake": "3.5.6",
        "gcc": "4.perocentos",
        "gpp": "gepusplas",
        "scons": "4.3.3"
        },
        "xmipp": {
        "branch": "agm_API",
        "updated": true
        },
        "returnCode": "0 con espacio",
        "logTail": "muchas lines"
        }' --request POST http://127.0.0.1:8000/api/attempts/ > file.html


'''
