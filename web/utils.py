#!/usr/bin/env python3
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
import requests, sys, concurrent.futures, pycountry
from typing import Union

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def fetch(url: str) -> Union[str, None]:
    """
    ### This function returns the country from an ip given an url with the ip embedded.

    #### Params:
    - utl (str): Url to look ip from.

    #### Returns:
    (str): Country name. None if there were any errors.
    """
    try:
        # Performing request
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        # Defining possible key names
        countryKeyList = ['country_name', 'country']

        # For every key name, check if exists
        for key in countryKeyList:
            if key in data:
                # Check if it is a country code or full country name
                if len(data[key]) < 4 and data[key]:
                    # Convert country code to full country name
                    return pycountry.countries.get(alpha_2=data[key]).name
                return data[key]
    # In case of exception, return None
    except (requests.exceptions.HTTPError, KeyError,
            requests.exceptions.RequestException,
            requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return None

def getCountry(ip: str) -> str:
    """
    ### This function returns the country an ip is from.

    #### Params:
    - ip (str): Ip to lookup.

    #### Returns:
    (str): Country name. If there were any errors, default is 'Unknown'.
    """
    # Defining list of urls to lookup from, for resiliency
    urls = [
        f"https://ipapi.co/{ip}/json/",
        f"https://ipinfo.io/{ip}/json",
        f"https://ipwhois.app/json/{ip}"
    ]

    # Sending concurrent requests to all the urls
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futureToUrl = {executor.submit(fetch, url): url for url in urls}
        for future in concurrent.futures.as_completed(futureToUrl):
            result = future.result()
            # Checking if result is valid, only valid results return
            if result is not None and result:
                return result

    # If there were errors, return default value
    return 'Unknown'