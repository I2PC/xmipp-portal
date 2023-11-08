from rest_framework.views import APIView
from .serializers import AttemptSerializer
from geocoder import ip
from .models import User, Xmipp, Version, Attempt
from rest_framework.response import Response
from rest_framework import status


class AttemptsView(APIView):
    serializer_class = AttemptSerializer()
    def get(self, request):
        json = {}

        return Response(json)

    def post(self, request, format='json'):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid() and format == 'json':
            data = serializer.data

            userID = data.id
            date = data.date
            os = data.os
            cuda = data.cuda
            cmake = data.cmake
            gcc = data.gcc
            gpp = data.gpp
            scons = data.scons
            branch = data.branch
            updated = data.updated
            returnCode = data.returnCode
            logTail = data.logTail

            userObj, created = User.objects.get_or_create(
                ID=userID,
                country=getCountryFromIP(getClientIP(request)))

            xmippObj, created = Xmipp.objects.get_or_create(
                branch=branch,
                updated=updated)

            versionsObj, created = Version.objects.get_or_create(
                os=os,
                cuda=cuda,
                cmake=cmake,
                gpp=gpp,
                gcc=gcc,
                scons=scons)


            attempt = Attempt(user=userObj,
                              version=versionsObj,
                              smipp=xmippObj,
                              date=date,
                              returnCode=returnCode,
                              logTail=logTail)
            attempt.save()

            return Response(AttemptSerializer(attempt).data, status=status.HTTP_201_CREATED)



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

'''


