from typing import Dict, Any
from pytsterrors.exception import TSTError
import json
import functools


def json_to_tst_error(json_string: str | bytes) -> TSTError:
    data = json.loads(json_string)
    if not isinstance(data, dict):
        raise TSTError("not-instance-of-dict", "JSON must have specific variables to serialize to TSTError exception")

    tag = data.get("tag")
    message = data.get("message")
    func_trace = data.get("func_trace")
    if not tag or not message or not func_trace :
        raise TSTError("not-correct-json", "JSON is not from TSTError")

    tst = TSTError(tag, message=message, can_inspect=False)
    tst.set_func_trace(func_trace)

    return tst


def tst_decorator(func):
    @functools.wraps(func)
    def tst_decorated(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            tag = type(e).__name__
            message = e.__str__()
            err = TSTError(tag, message)
            func_name = func.__name__
            trace = err.func_trace()
            trace[len(trace)-1] = trace[len(trace)-1].replace("tst_decorated", func_name)
            err.set_func_trace(trace)
            raise err

    return tst_decorated
