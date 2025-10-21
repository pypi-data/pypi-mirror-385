"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import json
from datetime import date, datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any

import shapely
from isodate import Duration, duration_isoformat
from shapely.geometry.base import BaseGeometry


def convert_to_serializable_value(obj: Any) -> Any:
    if isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%dT%H:%M:%SZ')
    if isinstance(obj, date):
        return obj.isoformat()
    if isinstance(obj, timedelta) or isinstance(obj, Duration):
        return duration_isoformat(obj)
    if isinstance(obj, Decimal):
        return str(obj)
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, bytes):
        return obj.decode()
    if isinstance(obj, BaseGeometry):
        return shapely.geometry.mapping(obj)

    # Serialize data models (not only, but mostly ORM) using to_dict.
    if hasattr(obj, 'to_dict'):
        return obj.to_dict()

    # Fallback to either the object's attribute dictionary or cast it to a string
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    return str(obj)


class DefaultJSONEncoder(json.JSONEncoder):
    def default(self, obj: Any):
        return convert_to_serializable_value(obj)
