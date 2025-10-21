# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def millis_to_local_time(millis: str, tz='America/Chicago'):
    # Millis to UTC seconds
    utc_seconds = int(millis) / 1000
    # Convert time im UTC...
    utc_time = datetime.fromtimestamp(utc_seconds, tz=timezone.utc)
    # ...to local time of the timezone; which will be in the daytime format.
    local_time = utc_time.astimezone(ZoneInfo(tz))
    return local_time
