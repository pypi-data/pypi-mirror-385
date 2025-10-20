from typing import *

__all__ = ["datarepr", "oxford"]


def datarepr(name: Any, /, *args: Any, **kwargs: Any) -> str:
    "This function allows for common sense representation."
    parts: list = list()
    x: Any
    for x in args:
        parts.append(repr(x))
    for x in kwargs.items():
        parts.append("%s=%r" % x)
    content: str = ", ".join(parts)
    ans: str = "%s(%s)" % (name, content)
    return ans


def oxford(*args: Any, conj: Any = "and", default: Any = "") -> Any:
    if len(args) == 0:
        return default
    ans: str
    if len(args) == 1:
        ans = "%r"
    elif len(args) == 2:
        ans = f"%r {conj} %r"
    else:
        ans = "%r, " * (len(args) - 1)
        ans += f"{conj} %r"
    ans %= args
    return ans
