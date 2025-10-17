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
from rest_framework import status
from django.db.models import Count, OuterRef, Subquery, F, IntegerField, Max, Q
from django_filters.rest_framework import DjangoFilterBackend
import django_filters
from rest_framework import generics
import threading
import logging
logger=logging.getLogger(__name__)

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

        if branch_name == 'devel' and returnCode != 0:
            continue

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
    logger.info(f"Attempts for release_id {release_id}")

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


class DetailedReleasePieChartView(APIView):

	def get(self, request, release_id, format: str = None) -> Response:
		"""
		This function receives a GET request and returns xmipp metrics (installations with no errors,
		installation with 1 previous error, ...) for a specific release branch, separated by user.

		Params:
		- request (Any): Django request.
		- release_id (int): Release id.
		- format (str): Optional. Request format.

		Returns:
		(Response): HTTP response with count info.
		"""
		# Step 1: Get all attempts for the given release_id, ordered by user and date
		attempts = Attempt.objects.filter(
			xmipp__id=release_id).order_by('user', 'date')
		attemptsDevel = Attempt.objects.exclude(
			xmipp__id__contains="v3.").order_by("user", "date")
		# Initialize a dictionary to store the final result for each category
		user_results = {
			'full_success': 0,
			'success_after_fails': 0,
			'fail': 0,
			'success_in_devel': 0
		}

		# Step 2: Group attempts (release and devel) by user
		user_attempts = {}
		user_attemptsDevel = {}

		for attempt in attempts:
			user = attempt.user  # Access the related User model through the ForeignKey
			logger.info(
				f"User: {user.id}, Attempt ID: {attempt.id}, ReturnCode: {attempt.returnCode}, Date: {attempt.date}")

			# Group attempts by user
			if user not in user_attempts:
				user_attempts[user] = []

			# Append the attempt to the user's list of attempts
			user_attempts[user].append(attempt)

		for attempt in attemptsDevel:
			user = attempt.user  # Access the related User model through the ForeignKey
			logger.info(
				f"User (in devel): {user.id}, Attempt ID: {attempt.id}, ReturnCode: {attempt.returnCode}, Date: {attempt.date}")

			# Group attempts by user
			if user not in user_attemptsDevel:
				user_attemptsDevel[user] = []

			# Append the attempt to the user's list of attempts
			user_attemptsDevel[user].append(attempt)


		# Step 3: Classify users based on their attempts
		for user, attempts_list in user_attempts.items():
			last_release_attempt_date = attempts_list[
				-1].date if attempts_list else None
			all_successful = True
			last_was_failed = False
			success_after_fail = False
			devel_candidate = False

			# Check if the last attempt is successful or failed, and if there are any previous failures
			for attempt in attempts_list:
				if attempt.returnCode != 0:  # Failed attempt
					all_successful = False
					last_was_failed = True
				elif last_was_failed:  # If there were previous failures and now it's successful
					success_after_fail = True


			# Classify the user based on their attempts
			if all_successful:
				user_results['full_success'] += 1  # Increment count for full success
			elif success_after_fail:
				user_results['success_after_fails'] += 1  # Increment count for success after fail
			elif last_was_failed:
				later_devel_attempts = [a for a in user_attemptsDevel[user]
				                        if a.date > last_release_attempt_date]
				if later_devel_attempts:
					latest_devel_attempt = max(later_devel_attempts, key=lambda x: x.date)
					if latest_devel_attempt.returnCode == 0:
						user_results['success_in_devel'] += 1
					else:
						user_results['fail'] += 1
				else:
					user_results['fail'] += 1

			# Log the classification of the user
			logger.info(f"User: {user.id} - Classification: {'full_success' if all_successful else 'success_after_fails' if success_after_fail else 'fail'}")

		# Step 4: Prepare the result to return as a JSON response

		result = []
		result.append({'category': 'full_success',
				'user_count': user_results['full_success']})
		result.append({'category': 'success_after_fails',
				'user_count': user_results['success_after_fails']})
		result.append({'category': 'success_in_devel',
				'user_count': user_results['success_in_devel']})
		result.append({'category': 'fail',
				'user_count': user_results['fail']})

		# Return the result as a JSON response
		return Response(result)


class AllReleasesPieChartView(APIView):

  def get(self, request):
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


class AttemptFilter(django_filters.FilterSet):
    returnCode = django_filters.NumberFilter(field_name="returnCode", lookup_expr="exact")

    returnCode_not = django_filters.NumberFilter(
        method="filter_returnCode_not",
        label="Return code (≠)"
    )

    class Meta:
        model = Attempt
        fields = [
            'user__userId',
	        'xmipp__branch',
	        'returnCode',
            'returnCode_not',
        ]

    def filter_returnCode_not(self, queryset, name, value):
        return queryset.exclude(returnCode=value)


class AttemptsFiltersAPIView(generics.ListAPIView):
    queryset = Attempt.objects.all()
    serializer_class = AttemptSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = AttemptFilter

class AttemptsView(APIView):
  """
    ### This class performs a custom processing of the requests received.
    """
  serializer_class = AttemptSerializer
  filterset_fields = ['userId', 'returnCode', 'xmipp__branch']

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
    for field in self.filterset_fields:
        value = request.query_params.get(field, None)
        if value is not None:
            # Soporte para relaciones (user__userId, xmipp__branch)
            queryset = queryset.filter(**{field: value})

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
    logger.info('ATTEMPT RECEIVED')

    # Get data from serializer
    serializer = self.serializer_class(data=request.data)

    # We only want to store valid requests, meaning serializer has to
    # validate and format has to be json (the only one we accept)
    if serializer.is_valid() and format == 'json':
      try:
          # Get serializer data into variables
          validatedData = serializer.validated_data
          userData = validatedData.get(ATTEMPT_USER)
          versionData = validatedData.get(ATTEMPT_VERSION)
          xmippData = validatedData.get(ATTEMPT_XMIPP)
          returnCode = validatedData.get(ATTEMPT_RETCODE)
          logTail = validatedData.get(ATTEMPT_LOGTAIL)
          #raise Exception('pa fuera')
          #self.collectObjectsData(request, userData, versionData, xmippData, returnCode, logTail)

          # Start background thread for additional calculations.
          # Without threads the calculations take like 10 secs (the timeout is set to 6 in the client side)
          thread = threading.Thread(target=self.collectObjectsData,
                                    args=(request, userData, versionData, xmippData, returnCode, logTail))
          thread.start()

          messageToReturn = (f'USER_ID: {userData[USER_ID]}  '
                             f'XMIPP_BRANCH: {xmippData[XMIPP_BRANCH]} '
                             f'XMIPP_INSTALLED: {xmippData[XMIPP_INSTALLED]} '
                             f'VERSION_OS: {versionData[VERSION_OS]}  '
                             f'VERSION_GCC: {versionData[VERSION_GCC]}  '
                             f'VERSION_CUDA: {versionData[VERSION_CUDA]}')
          # Return a response contaning the attempt data

          logger.info(f'ATTEMPT PROCESSED')
          return Response({'data': messageToReturn})
      except Exception as e:
          logger.error(f'There was an error saving data', exc_info=e)


    else:
      # In case received data does not validate, return a response with some info
      logger.error('if serializer.is_valid() and format == json: False: {}\n'.format(serializer.errors))
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
      logger.info(f'ATTEMPT SAVED')

class VersionCUDAView(APIView):#TODO
	"""
	### Returns the count of CUDA and GPP versions per Xmipp release (branch),
	filtered to only include branches starting with 'v3'.

	#### Example response:
	[
	    {"release": "v3.22", "cuda": "11.2", "gpp": "9.3", "count": 15},
	    {"release": "v3.23", "cuda": "12.1", "gpp": "10.2", "count": 4}
	]
	"""
	def get(self, request, format=None) -> Response:
		queryset = (
			Attempt.objects.filter(
				returnCode=0,
				xmipp__branch__startswith="v3."  # <-- filtro añadido
			)
			.values(
				"xmipp__branch",  # release (rama de Xmipp)
				"version__cuda",  # versión CUDA
			)
			.annotate(count=Count("id", distinct=True))
			.order_by("xmipp__branch", "version__cuda")
		)

		data = [
			{
				"release": item["xmipp__branch"],
				"cuda": item["version__cuda"],
				"count": item["count"],
			}
			for item in queryset
		]
		return Response(data)


class VersionGPPView(APIView):
	"""
	### Returns the count of CUDA and GPP versions per Xmipp release (branch),
	filtered to only include branches starting with 'v3'.

	#### Example response:
	[
	    {"release": "v3.22", "cuda": "11.2", "gpp": "9.3", "count": 15},
	    {"release": "v3.23", "cuda": "12.1", "gpp": "10.2", "count": 4}
	]
	"""
	def get(self, request, format=None) -> Response:
		queryset = (
			Attempt.objects.filter(
				returnCode=0,
				xmipp__branch__startswith="v3."  # <-- filtro añadido
			)
			.values(
				"xmipp__branch",  # release (rama de Xmipp)
				"version__gpp",  # versión G++
			)
			.annotate(count=Count("id", distinct=True))
			.order_by("xmipp__branch", "version__gpp")
		)

		data = [
			{
				"release": item["xmipp__branch"],
				"gpp": item["version__gpp"],
				"count": item["count"],
			}
			for item in queryset
		]

		return Response(data)

class FailedAttemptsView(APIView):
    def get(self, request, format=None):
        failed_attempts = Attempt.objects.exclude(returnCode=0).order_by('-date')
        data = [
            {
                "id": attempt.id,
                "date": attempt.date,
                "returnCode": attempt.returnCode,
	            "branch": attempt.xmipp.branch,
                "logTail": attempt.logTail,
            }
            for attempt in failed_attempts
        ]
        return Response(data)


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

'''
 curl --header "Content-Type: application/json" -X POST --data '{
"user": {
"userId": "EstrellaTest"
}, 
"version": {
"os": "SBGrid", 
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
"branch": "SBGrid", 
"updated": true, 
"installedByScipion": true
}, 
"returnCode": 0, 
"logTail": null
}' --request POST https://xmipp.i2pc.es/api/attempts/ > file.html
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
  
  