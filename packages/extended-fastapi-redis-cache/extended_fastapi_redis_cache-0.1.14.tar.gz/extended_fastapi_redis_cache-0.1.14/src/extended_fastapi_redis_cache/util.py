import json
from datetime import date, datetime
from decimal import Decimal

import orjson
from dateutil import parser
from pydantic import BaseModel

DATETIME_AWARE = "%m/%d/%Y %I:%M:%S %p %z"
DATE_ONLY = "%m/%d/%Y"

ONE_HOUR_IN_SECONDS = 3600
ONE_DAY_IN_SECONDS = ONE_HOUR_IN_SECONDS * 24
ONE_WEEK_IN_SECONDS = ONE_DAY_IN_SECONDS * 7
ONE_MONTH_IN_SECONDS = ONE_DAY_IN_SECONDS * 30
ONE_YEAR_IN_SECONDS = ONE_DAY_IN_SECONDS * 365

SERIALIZE_OBJ_MAP = {
    str(datetime): parser.parse,
    str(date): parser.parse,
    str(Decimal): Decimal,
}


class BetterJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, BaseModel):
            return json.loads(obj.json())
        elif isinstance(obj, datetime):
            return obj.strftime(DATETIME_AWARE)
        elif isinstance(obj, date):
            return obj.strftime(DATE_ONLY)
        elif isinstance(obj, Decimal):
            return float(obj)
        else:  # pragma: no cover
            return super().default(obj)


def object_hook(obj):
    if "_spec_type" not in obj:
        return obj
    _spec_type = obj["_spec_type"]
    if _spec_type not in SERIALIZE_OBJ_MAP:  # pragma: no cover
        raise TypeError(f'"{obj["val"]}" (type: {_spec_type}) is not JSON serializable')
    return SERIALIZE_OBJ_MAP[_spec_type](obj["val"])


def serialize_json(json_dict):
    # we try to use the orjson.dumps
    # if that doesn't work, default to json.dumps
    # orjson doesn't support cls for custom serialization, so that's why we have to use .dict() first
    if isinstance(json_dict, BaseModel):
        json_dict = json_dict.dict()
    try:
        return orjson.dumps(json_dict)
    except Exception as e:
        return json.dumps(json_dict, cls=BetterJsonEncoder)

def deserialize_json(json_str):
    return orjson.loads(json_str)
