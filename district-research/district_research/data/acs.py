"""
Code to interact with American Community Survey data using Census API.
Is only for five year estimates. We will use this in place of the python package
census when they do not support something.
"""

import logging

import requests
import pandas as pd

def get_acs_data_table(api_key, est, year, geo, geo_val, *codes):

    codes_str = ','.join(list(codes) + [x + 'A' for x in codes])
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
    return pd.DataFrame(acs_response[1:], columns=acs_response[0])
