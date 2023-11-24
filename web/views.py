from rest_framework.views import APIView
from .serializers import AttemptSerializer
from geocoder import ip
from .models import User, Xmipp, Version, Attempt
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status


class AttemptsView(APIView):
    serializer_class = AttemptSerializer


    def get(self, request, format=None):
        attempts = [attempt.user for attempt in Attempt.objects.all()]
        return JsonResponse({'Attempt': attempts})

    def post(self, request, format='json'):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid() and format == 'json':
            validated_data = serializer.validated_data
            user_data = validated_data.get('user')
            version_data = validated_data.get('version')
            xmipp_data = validated_data.get('xmipp')
            returnCode = validated_data.get('returnCode')
            logTail = validated_data.get('logTail')

            userObj, created = User.objects.update_or_create(
                userId=user_data['userId'],
                defaults={'country': user_data['country']})

            xmippObj, created = Xmipp.objects.get_or_create(
                branch=xmipp_data['branch'],
                updated=xmipp_data['updated'])

            versionsObj, created = Version.objects.get_or_create(
                os=version_data['os'],
                cudaVersion=version_data['cudaVersion'],
                cmakeVersion=version_data['cmakeVersion'],
                gppVersion=version_data['gppVersion'],
                gccVersion=version_data['gccVersion'],
                sconsVersion=version_data['sconsVersion'])

            attempt = Attempt(user=userObj,
                              version=versionsObj,
                              xmipp=xmippObj,
                              #date=date,
                              returnCode=returnCode,
                              logTail=logTail)
            attempt.save()
            return Response({'data': AttemptSerializer(attempt).data})

        else:
            print('HOOOOOOOOOOOOOOLA')
            print('ERRORS: {}\n'.format(serializer.errors['user']))
            return Response({'Holi ': 0,
                             'isValid': serializer.is_valid(),
                             'isJSON': format == 'json'},
                             status=status.HTTP_400_BAD_REQUEST)


#########UTILS

def getClientIP(request):
  xForwardedFor = request.META.get('HTTP_X_FORWARDED_FOR')
  return xForwardedFor.split(',')[0] if xForwardedFor else request.META.get('REMOTE_ADDR')


def getCountryFromIP(ipAddress):
    ipAddress = ip(ipAddress)
    if ipAddress is not None:
        return ipAddress.country
    else:
        return 'Unkown'


'''
--data '{
       "user": {
         "userId": "hashMachine5",
         "country": "someCountry"
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


