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

from rest_framework.views import APIView
from .serializers import AttemptSerializer
from .models import User, Xmipp, Version, Attempt
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from .utils import getClientIp, getCountryFromIp

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
      validatedData = serializer.validatedData
      userData = validatedData.get('user')
      versionData = validatedData.get('version')
      xmippData = validatedData.get('xmipp')
      returnCode = validatedData.get('returnCode')
      logTail = validatedData.get('logTail')

      # Obtaining country from sender's ip
      country = getCountryFromIp(getClientIp(request))

      # Creating user object
      userObj = User.objects.update_or_create(
        userId=userData['userId'],
        defaults={'country': country}
      )[0]

      # Creating xmipp object
      xmippObj = Xmipp.objects.get_or_create(
        branch=xmippData['branch'],
        updated=xmippData['updated']
      )[0]

      # Creating version object
      versionsObj = Version.objects.get_or_create(
        os=versionData['os'],
        cudaVersion=versionData['cudaVersion'],
        cmakeVersion=versionData['cmakeVersion'],
        gppVersion=versionData['gppVersion'],
        gccVersion=versionData['gccVersion'],
        sconsVersion=versionData['sconsVersion']
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
      print('HOOOOOOOOOOOOOOLA')
      print('ERRORS: {}\n'.format(serializer.errors['user']))
      return Response(
        {
          'Holi ': 0,
          'isValid': serializer.is_valid(),
          'isJSON': format == 'json'
        },
        status=status.HTTP_400_BAD_REQUEST
      )

'''
--data '{
       "user": {
         "userId": "hashMachine5"
       },
       "version": {
         "os": "Centor",
         "cudaVersion": "NoSequeeseso",
         "cmakeVersion": "3.5.6",
         "gccVersion": "4.perocentos",
         "gppVersion": "gepusplas",
         "sconsVersion": "4.3.3"
       },
       "xmipp": {
         "branch": "agm_API",
         "updated": true
       },
       "returnCode": "0 con espacio",
       "logTail": "muchas lines"
     }'      http://127.0.0.1:8000/web/attempts/ >salida.html


'''
