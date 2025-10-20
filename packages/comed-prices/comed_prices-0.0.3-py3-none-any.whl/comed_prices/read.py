# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""

import requests
from utils import millis_to_local_time

BASE_URL = 'https://hourlypricing.comed.com/api'


def current_hour_average_price(tz='America/Chicago'):
    response = requests.get(
        url=BASE_URL,
        params={
            'type': 'currenthouraverage',
            'format': 'json'
        }
    )
    if not response.ok:
        raise Exception('Could not get current hour average price')

    # The first item in the useless (here) list.
    result = response.json()[0]

    # Convert strings to numbers
    price = float(result['price'])
    utc_millis = result['millisUTC']

    local_time = millis_to_local_time(utc_millis, tz)
    return price, local_time


def five_minute_prices(start=None, end=None, tz='America/Chicago'):
    '''
    start: YYYYMMDDhhmm
    end: YYYYMMDDhhmm 202510192330
    '''

    response = requests.get(
        url=BASE_URL,
        params={
            'type': '5minutefeed',
            'datestart': start,
            'dateend': end
        }
    )
    if not response.ok:
        raise Exception('Could not get current list of five minute prices')

    # The first item in the useless (here) list.
    data = response.json()

    prices = []
    for d in data:
        new_dict = d.copy()  # Shallow copy to avoid modifying original
        new_dict['price'] = float(new_dict['price'])
        new_dict['local_time'] = millis_to_local_time(new_dict['millisUTC'], tz)
        del new_dict['millisUTC']
        prices.append(new_dict)

    return prices


if __name__ == '__main__':
    print('You have launched __main__')
    p = five_minute_prices(tz='America/Chicago')
    ...