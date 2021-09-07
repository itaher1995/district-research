"""
Code to interact with American Community Survey data using Census API.
Is only for five year estimates. We will use this in place of the python package
census when they do not support something.
"""

import requests
import pandas as pd

def get_acs_data_table(api_key, est, year, geo, geo_val, *codes):
    """Creates a table of socioeconomic indicators for either ACS1 or ACS5 
        indicators for a given year for certain geographic levels. For example,
        we can create ACS5 socioeconomic estimates for ZCTAs (Census version of
        zip codes) in the year 2019.

        Args:
            api_key (str): The API Key used to access ACS data
            est (str): The type of estimate. Is either 'acs1' or 'acs5'
            year (int): The year to grab estimates for
            geo (str): The type of geography to grab data for
            geo_val (str): A comma delimited string of the geographies to grab
                data for. If one wants all just put '*'
            codes (str): args that indicate the different census socioeconomic
                codes.
        
        Returns
            A DataFrame with every geography and its associated socioeconomic 
                values.
    """

    # removing the voting age population citizens metric for years prior bc
    # the census doesn't seem to have it for any year after this one.
    if int(year) >= 2015:
        codes_str = ','.join(list(codes) + [x + 'A' for x in codes])
    else:
        codes_str = ','.join([
            x for x in codes if x not in ['DP05_0087E', 'DP05_0082E']] 
            + [x + 'A' for x in codes if x not in ['DP05_0087E', 'DP05_0082E']
        ])

    geo_formatted = geo.lower().replace(' ', '%20')
    url = (
        'https://api.census.gov/data/{0}'
        '/acs/{1}/profile?get={2}&for={3}:{4}&key={5}'
       .format(year, est, codes_str, geo_formatted, geo_val, api_key)
    )

    response = requests.get(url)

    # if the status code is anything but 200 (e.g. a 404 error) then this
    # function should fail. This may happen if any of the params passed to this
    # function results in a failed request.
    assert response.status_code == 200

    acs_response = response.json()
    df = pd.DataFrame(acs_response[1:], columns=acs_response[0])
    df['YEAR'] = year
    return df
