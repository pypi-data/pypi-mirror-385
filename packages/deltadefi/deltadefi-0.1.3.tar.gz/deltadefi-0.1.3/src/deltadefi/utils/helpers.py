from urllib.parse import urlencode

from deltadefi.error import (
    ParameterRequiredError,
    ParameterTypeError,
    ParameterValueError,
)


def clean_none_value(d) -> dict:
    out = {}
    for k in d:
        if d[k] is not None:
            out[k] = d[k]
    return out


def check_required_parameter(value, name):
    if not value and value != 0:
        raise ParameterRequiredError([name])


def check_required_parameters(params):
    """Validate multiple parameters
    params = [
        ['btcusdt', 'symbol'],
        [10, 'price']
    ]

    """
    for p in params:
        check_required_parameter(p[0], p[1])


def check_enum_parameter(value, enum_class):
    if value not in {item.value for item in enum_class}:
        raise ParameterValueError([value])


def check_type_parameter(value, name, data_type):
    if value is not None and not isinstance(value, data_type):
        raise ParameterTypeError([name, data_type])


def encoded_string(query):
    return urlencode(query, True).replace("%40", "@")
