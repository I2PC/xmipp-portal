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
        print('serializer.is_valid(): {}'.format(serializer.is_valid()))
        print('''format == 'json': {}'''.format(format == 'json'))

        if serializer.is_valid() and format == 'json':
            print('serializer.errors: {}'.format(serializer.errors))

            validated_data = serializer.validated_data
            user_data = validated_data.get('user')
            version_data = validated_data.get('version')
            xmipp_data = validated_data.get('xmipp')
            returnCode = validated_data.get('returnCode')
            logTail = validated_data.get('logTail')

            print('Espabila')


            #userID = serializer.user.ID
            #date = data.date TODO manage date from django
            #country = data.user.country TODO manage country from django
            #os = serializer.version.os
            #cuda = serializer.version.cudaVersion
            #cmake = serializer.version.cmakeVersion
            #gcc = serializer.version.gccVersion
            #gpp = serializer.version.gppVersion
            #scons = serializer.version.sconsVersion
            #branch = serializer.xmipp.branch
            #updated = serializer.xmipp.updated
            #returnCode = serializer.attempt.returnCode
            #logTail = serializer.attempt.logTail

            userObj, created = User.objects.get_or_create(
                ID=user_data['ID'],
                country='CoreaDelNorte')

            print('Hello2')

            xmippObj, created = Xmipp.objects.get_or_create(
                branch=xmipp_data['branch'],
                updated=xmipp_data['updated'])
            print('Hello3')

            versionsObj, created = Version.objects.get_or_create(
                os=version_data['os'],
                cudaVersion=version_data['cudaVersion'],
                cmakeVersion=version_data['cmakeVersion'],
                gppVersion=version_data['gppVersion'],
                gccVersion=version_data['gccVersion'],
                sconsVersion=version_data['sconsVersion'])
            print('Hello4')


            attempt = Attempt(user=userObj,
                              version=versionsObj,
                              xmipp=xmippObj,
                              #date=date,
                              returnCode=returnCode,
                              logTail=logTail)
            attempt.save()


            return Response({'data': AttemptSerializer(attempt).data})
            #return JsonResponse(AttemptSerializer(attempt).data, status=status.HTTP_201_CREATED)

        else:
            print('serializer.errors: {}'.format(serializer.errors))
            return Response({'Holi ': 0}, status=status.HTTP_400_BAD_REQUEST)


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
request json example:

    {
      'id': id,
      'date': date,
      'os': os,
      'cuda': cuda,
      'cmake': cmake,
      'gcc': gcc,
      'gpp': gpp,
      'scons': scons,
      'branch': branch,
      'updated': updated,
      'returnCode': returnCode,
      'logTail': logTail
    }
curl --header "Content-Type: application/json" -X POST --data '{"user":"hashMachine","os":"Ubuntur","cuda":"NoSequeeseso","cmake":"3.5.6","gcc":"4.perocentos","gpp":"gepusplas","scons":"4.3.3","branch":"agm_API","updated":"claroMakina","returnCode":"0 con espacio ", "logTail":"muchas lines"}' --request POST http://127.0.0.1:8000/web/attempts/

curl --header "Content-Type: application/json" \
     -X POST \
     --data '{
       "user": {
         "ID": "hashMachine",
         "country": "someCountry"
       },
       "version": {
         "os": "Ubuntur",
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
     }' \
     http://127.0.0.1:8000/web/attempts/




'''


