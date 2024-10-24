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
from django.db.models import Count, OuterRef, Subquery, F, IntegerField, Max, Q

# Self imports
from .models import User, Xmipp, Version, Attempt
from .serializers import AttemptSerializer, XmippSerializer
from .utils import getClientIp, getCountryFromIp
from .constants import USER_ID, USER_COUNTRY, XMIPP_BRANCH, XMIPP_UPDATED, VERSION_OS, VERSION_CUDA,\
	VERSION_CMAKE, VERSION_GCC, VERSION_GPP, ATTEMPT_USER, ATTEMPT_VERSION, ATTEMPT_XMIPP,\
	ATTEMPT_RETCODE, ATTEMPT_LOGTAIL, VERSION_ARCHITECTURE, VERSION_MPI, VERSION_PYTHON,\
	VERSION_SQLITE, VERSION_JAVA, VERSION_HDF5, VERSION_JPEG

class InstalledBranchesPieChartView(APIView):

  def get(self, request, format: str=None) -> Response:
    """
    ### This function receives a GET request and returns xmipp branches successfully installed (one per user).
    Developers' branches (which do not include "release" or "devel" in their name) are included in devel count.

    #### Params:
    - request (Any): Django request.
    - format (str): Optional. Request format.

    #### Returns:
    (Response): HTTP response with count info.
    """
    # Get more recent attempt per user
    subquery = Attempt.objects.filter(user=OuterRef('user')).order_by('-date')

    # Filter attempts that match those latest dates
    latest_attempts = Attempt.objects.annotate(
      latest_date=Subquery(subquery.values('date')[:1])
      ).filter(date=F('latest_date'))
    
    # Separate querysets for 'release' and 'devel'
    release_attempts = latest_attempts.filter(
        returnCode=0,
        xmipp__branch__iregex=r'release'
    ).values("xmipp__branch").annotate(release_count=Count('id'))

    devel_attempts = latest_attempts.exclude(
        xmipp__branch__iregex=r'release'
    ).values("xmipp__branch").annotate(release_count=Count('id'))

    # Combine both querysets into one
    combined_queryset = list(release_attempts) + list(devel_attempts)


    # Process combined queryset to include all developers' branches in devel count
    result = []
    devel_count = 0
    
    for attempt in combined_queryset:
        branch_name = attempt['xmipp__branch']
        count = attempt['release_count']

        if 'release' in branch_name:
            # Add release branches as they are
            result.append({
                "xmipp__branch": branch_name,
                "release_count": count
            })
        else:
            # Sum all non-release branches under 'devel'
            devel_count += count

    # Append the 'devel' branch with the total count of non-release branches
    if devel_count > 0:
        result.append({
            "xmipp__branch": "devel",
            "release_count": devel_count
        })

    # Return the final JSON response
    return Response(result)
  
class ReleasePieChartView(APIView):

  def get(self, request, release_id, format: str=None) -> Response:
    """
    ### This function receives a GET request and returns xmipp metrics (installations with no errors, 
    # installation with 1 previous error, ...) for a specific release branch.

    #### Params:
    - request (Any): Django request.
    - release_id (int): Release id. 
    - format (str): Optional. Request format.

    #### Returns:
    (Response): HTTP response with count info.
    """
    # Step 1: Get the latest date for each user for the given release_id
    latest_dates = Attempt.objects.filter(xmipp__id=release_id).values('user').annotate(latest_date=Max('date'))

    # Step 2: Filter successful attempts that match the latest dates
    latest_attempts = Attempt.objects.filter(
        xmipp__id=release_id,
        returnCode=0,
        date__in=[item['latest_date'] for item in latest_dates]
    )

    # Step 3: Annotate the count of previous failures before the successful attempt
    previous_failures = Attempt.objects.filter(
        xmipp__id=release_id,
        user=OuterRef('user'),
        date__lt=OuterRef('date')
    ).exclude(returnCode=0).values('user').annotate(count=Count('id')).values('count')

    latest_attempts = latest_attempts.annotate(
        previous_failures=Subquery(previous_failures, output_field=IntegerField())
    )

    # Step 4: Group by number of previous failures and count the occurrences
    attempt_counts = latest_attempts.values('previous_failures').annotate(count=Count('id')).order_by('previous_failures')

    # Return the result as a JSON response
    return Response(attempt_counts)
  
class AllReleasesPieChartView(APIView):

  def get(self, request, format=None):
    """
    ### This function receives a GET request and returns xmipp metrics (installations with no errors, 
    # installation with 1 previous error, ...) for all xmipp releases.

    #### Params:
    - request (Any): Django request.
    - format (str): Optional. Request format.

    #### Returns:
    (Response): HTTP response with count info.
    """

    # Step 1: Get the branches from the query parameters
    branches = request.query_params.get('branches', '')
    branches_list = branches.split(',')

    # Step 2: Annotate the latest date of a successful attempt per user per release
    latest_attempt_dates = Attempt.objects.filter(
        returnCode=0,
        xmipp__branch__in=branches_list  # Filter by the list of branches
    ).values('user', 'xmipp__id').annotate(latest_date=Max('date'))

    # Step 3: Use the annotated latest dates to filter the latest successful attempts
    latest_attempts = Attempt.objects.filter(
        Q(date__in=[item['latest_date'] for item in latest_attempt_dates]),
        returnCode=0,
        xmipp__branch__in=branches_list  # Filter by the list of branches
    )

    # Step 4: Count previous failures before each latest successful attempt
    previous_failures_counts = []
    for attempt in latest_attempts:
        previous_failures = Attempt.objects.filter(
            user=attempt.user,
            xmipp__id=attempt.xmipp.id,
            date__lt=attempt.date
        ).exclude(returnCode=0).count()

        previous_failures_counts.append({
            'xmipp__id': attempt.xmipp.id,
            'previous_failures': previous_failures,
        })

    # Step 5: Aggregate counts across all releases
    summary = {}
    for entry in previous_failures_counts:
        failures = entry['previous_failures']
        summary[failures] = summary.get(failures, 0) + 1

    # Convert the result to the format expected by the Response
    formatted_result = [{'previous_failures': k, 'total_count': v} for k, v in summary.items()]

    return Response(formatted_result)
  

class CountryBarChartView(APIView):

  def get(self, request, format: str=None) -> Response:
    """
    ### This function receives a GET request and returns all users per country values.

    #### Params:
    - request (Any): Django request.
    - format (str): Optional. Request format.

    #### Returns:
    (Response): HTTP response with count info.
    """
    # Create a queryset to filter users with successful attempts and 
    # aggregate them to get users per country
    queryset = User.objects.filter(attempts__returnCode=0).values("country") \
      .annotate(users_count=Count('id', distinct=True))

    # Return users as JSON
    return Response(queryset)
class AttemptsView(APIView):
  """
	### This class performs a custom processing of the requests received.
	"""
  serializer_class = AttemptSerializer

  def get(self, request, format: str=None) -> Response:
    """
    ### This function receives a GET request and returns all attempts's info.

    #### Params:
    - request (Any): Django request.
    - format (str): Optional. Request format.

    #### Returns:
    (Response): HTTP response with attempts's info.
    """
    # Get queryset with all the attempts in database and serialize it
    queryset = Attempt.objects.all()
    serializer = AttemptSerializer(queryset, many = True)

    # Return attempts as JSON
    return Response(serializer.data)

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
        mpi=versionData[VERSION_MPI],
        python=versionData[VERSION_PYTHON],
        sqlite=versionData[VERSION_SQLITE],
        java=versionData[VERSION_JAVA],
        hdf5=versionData[VERSION_HDF5],
        jpeg=versionData[VERSION_JPEG],      
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
        },
        "xmipp": {
        "branch": "agm_API",
        "updated": true
        },
        "returnCode": "0",
        "logTail": "muchas lines"
        }' --request POST http://127.0.0.1:8000/api/attempts/ > file.html


'''

class XmippView(APIView):

  serializer_class = XmippSerializer

  def get(self, request, format: str=None) -> Response:
    """
    ### This function receives a GET request and returns all xmipp branches' info.

    #### Params:
    - request (Any): Django request.
    - format (str): Optional. Request format.

    #### Returns:
    (Response): HTTP response with xmipp branches' info.
    """
    # Get queryset with all the attempts in database and serialize it
    queryset = Xmipp.objects.all()
    serializer = XmippSerializer(queryset, many = True)

    # Return attempts as JSON
    return Response(serializer.data)
  
  