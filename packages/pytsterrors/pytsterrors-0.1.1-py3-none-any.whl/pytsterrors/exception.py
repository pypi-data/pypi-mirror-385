import json
import inspect
import copy
import typing


class TSTError(Exception):
    _func_trace: list[str]
    _message: str
    _tag: str

    def __init__(
        self,
        tag: str,
        message: str,
        can_inspect=True,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._func_trace = []
        self._message = message
        self._tag = tag

        if can_inspect:
            for frame_info in inspect.stack()[1:]:
                func_name = frame_info.function
                if func_name == "<module>":
                    continue

                frame = frame_info.frame
                if "self" in frame.f_locals:
                    class_name = frame.f_locals["self"].__class__.__name__
                    self._func_trace.append(f"{class_name}.{func_name}")
                else:
                    self._func_trace.append(func_name)

            self._func_trace[0] = f"{self._func_trace[0]}.{tag}"
            self._func_trace.reverse()

    def __str__(self) -> str:
        if self._message:
            return self._message
        else:
            return super().__str__()

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        return {
            "func_trace": self._func_trace,
            "message": self._message,
            "tag": self._tag
        }

    def func_trace(self) -> list[str]:
        return self._func_trace

    def message(self) -> str:
        return self._message

    def tag(self) -> str:
        return self._tag

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def routes(self, *func_names: str) -> bool:
        return self._func_trace == list(func_names)

    def sub_routes(self, *func_names: str) -> bool:
        param_fns = list(func_names)
        # empty sublist will be always false as there is no reason to
        # check with empty list
        if not param_fns:
            return False

        i = 0
        m = len(param_fns)
        for elem in self._func_trace:
            if i < m and elem == param_fns[i]:
                i += 1
            if i == m:
                return True
        return False

    def set_func_trace(
        self, func_trace: list[str] 
    ) -> None:
        self._func_trace = func_trace

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TSTError):
            return False
        return self.func_trace() == other.func_trace() and \
            self.message() == other.message() and \
            self.tag() == other.tag() and \
            self.message() == other.message()