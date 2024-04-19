from attrs.exceptions import NotAnAttrsClassError


class Counter:
    def __init__(self):
        self._count = 0

    def __call__(self):
        self._count += 1
        return self._count

    @property
    def count(self):
        return self._count


def model_fields(cls) -> tuple:
    if not isinstance(cls, type):
        msg = "Passed object must be a class."
        raise TypeError(msg)
    attrs = getattr(cls, "__attrs_attrs__", None)
    if attrs is None:
        msg = f"{cls!r} is not an attrs-decorated class."
        raise NotAnAttrsClassError(msg)
    return tuple(a.name for a in attrs)
