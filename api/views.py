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
import threading

# Self imports
from .models import User, Xmipp, Version, Attempt
from .serializers import AttemptSerializer, XmippSerializer
from .utils import getClientIp, getCountryFromIp
from .constants import USER_ID, USER_COUNTRY, XMIPP_BRANCH, XMIPP_UPDATED, XMIPP_INSTALLED, VERSION_OS, VERSION_CUDA,\
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
        xmipp__branch__iregex=r'v3.'
    ).values("xmipp__branch").annotate(release_count=Count('id'))

    devel_attempts = latest_attempts.exclude(
        xmipp__branch__iregex=r'v3.'
    ).values("xmipp__branch").annotate(release_count=Count('id'))

    # Combine both querysets into one
    combined_queryset = list(release_attempts) + list(devel_attempts)


    # Process combined queryset to include all developers' branches in devel count
    result = []
    devel_count = 0
    
    for attempt in combined_queryset:
        branch_name = attempt['xmipp__branch']
        count = attempt['release_count']

        if 'v3.' in branch_name:
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
  

class InstalledBranchesTimeChartView(APIView):

  def get(self, request, format: str=None) -> Response:
    """
    ### This function receives a GET request and returns xmipp branches successfully installed (one per user) over time.
    Developers' branches (which do not include "release" or "devel" in their name) are included in devel liist.

    #### Params:
    - request (Any): Django request.
    - format (str): Optional. Request format.

    #### Returns:
    (Response): HTTP response with attempts info.
    """
    # Subquery to get the most recent attempt for each user and returnCode
    recent_attempts = (
        Attempt.objects
        .annotate(latest_date=Max('date'))  # Get latest attempt date for each user/returnCode
        .values('user', 'returnCode', 'xmipp__branch')  # Group by user, returnCode, and branch
        .annotate(date=Max('date'))  # Ensure only the most recent attempt per combination is selected
    )
    # Process combined queryset to include all developers' branches in devel list
    result = []
    devel_list = []
    
    for attempt in recent_attempts:
        branch_name = attempt['xmipp__branch']
        attempt_date = attempt['date']
        returnCode = attempt['returnCode']

        if 'v3.' in branch_name:
            # Add release branches as they are
            result.append({
                "xmipp__branch": branch_name,
                "date": attempt_date,
                "returnCode": returnCode
            })
        else:
            # Sum all non-release branches under 'devel'
            result.append({
                "xmipp__branch": "devel",
                "date": attempt_date,
                "returnCode": returnCode
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
    # Step 1: Get all attempts for the given release_id
    attempts = Attempt.objects.filter(xmipp__id=release_id)

    # Step 2: Get successful attempts
    successfull_attempts = Attempt.objects.filter(
        xmipp__id=release_id,
        returnCode=0,
    ).count()

    fail_attempts = Attempt.objects.filter(
        xmipp__id=release_id,
    ).exclude(returnCode=0).count()

    result = []
    result.append({
        "successfull_installations": successfull_attempts,
    })

    result.append({
        "failed_installations": fail_attempts,
    })

    # Return the result as a JSON response
    return Response(result)
  
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

      # Start background thread for additional calculations
      thread = threading.Thread(target=self.collectObjectsData,
                                args=(request, userData, versionData, xmippData, returnCode, logTail))
      thread.start()

      messageToReturn = (f'{userData[USER_ID]}, '
                         f'{xmippData[XMIPP_BRANCH]},'
                         f' {xmippData[XMIPP_INSTALLED]},'
                         f' {versionData[VERSION_OS]},'
                         f'{versionData[VERSION_GCC]},'
                         f'{versionData[VERSION_CUDA]}')
      # Return a response contaning the attempt data
      return Response({'data': messageToReturn})
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



  def collectObjectsData(self, request, userData, versionData, xmippData, returnCode, logTail):
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
          updated=xmippData[XMIPP_UPDATED],
          installedByScipion=xmippData[XMIPP_INSTALLED]
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
                        # date=date,
                        returnCode=returnCode,
                        logTail=logTail
                        )

      # Saving attempt
      attempt.save()



'''
 curl --header "Content-Type: application/json" -X POST --data '{
"user": {
"userId": "machineHash"
}, 
"version": {
"os": "Ubuntu 22.04.5 LTS", 
"architecture": "fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc art arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc cpuid aperfmperf pni pclmulqdq dtes64 monitor ds_cpl vmx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm 3dnowprefetch cpuid_fault epb ssbd ibrs ibpb stibp ibrs_enhanced tpr_shadow flexpriority ept vpid ept_ad fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid mpx rdseed adx smap clflushopt intel_pt xsaveopt xsavec xgetbv1 xsaves dtherm ida arat pln pts hwp hwp_notify hwp_act_window hwp_epp vnmi pku ospke md_clear flush_l1d arch_capabilities", 
"cuda": "11.7.64", 
"cmake": "3.22.1", 
"gcc": "GNU-11.4.0", 
"gpp": "GNU-11.4.0", 
"mpi": "3.1", 
"python": "3.8.15", 
"sqlite": "3.46.0", 
"java": "11.0.25", 
"hdf5": "1.10.6", 
"jpeg": "80"
}, 
"xmipp": {
"branch": "agm_ScipionField", 
"updated": true, 
"installedByScipion": true
}, 
"returnCode": 0, 
"logTail": null
}' --request POST http://127.0.0.1:8000/api/attempts/ > file.html
'''
#https://xmipp.i2pc.es/api/attempts/

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
  
  