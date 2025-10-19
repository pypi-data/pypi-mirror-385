from .slicer_exceptions import SlicerArgumentException


def validate_duration(time) -> tuple:
    """
    Args:
        time: type=str/int
    Returns:
        tuple(time, unit)
    """
    if isinstance(time, (int, float)):
        return time, "sec"
    elif isinstance(time, str):
        time = time.lower()
        if time.endswith("sec"):
            _time = float(time.replace("sec", ""))
            return _time, "sec"
        elif time.endswith("min"):
            _time = float(time.replace("min", ""))
            return _time, "min"
        else:
            raise SlicerArgumentException(
                "Invalid duration -> Must be an intenger or take one of ('sec', 'min') as postfix."
            )


def validate_size(size) -> tuple:
    """
    Args:
        size: type=str/int
    Returns:
        tuple(size, unit)
    """
    if isinstance(size, (int, float)):
        return int(size), "kb"
    elif isinstance(size, str):
        size = size.lower()
        if size.endswith("kb"):
            _size = int(size.split("kb")[0])
            return _size, "kb"
        elif size.endswith("mb"):
            _size = int(size.split("mb")[0])
            return _size, "mb"
        else:
            raise SlicerArgumentException(
                "Invalid size -> Must be an intenger or take one of ('kb', 'mb') as postfix."
            )


def validate_time_range(start: None, end=None) -> tuple:
    """
    Args:
        start: type=str/int
        end: type=str/int
    Returns:
        tuple(start, end)
    """

    if isinstance(start, (int, float)) and isinstance(end, (int, float)):
        # start_ = start if start != 0 else 0
        #  end_ = end if end != -1 else -1
        is_range = any((start > 0, end != -1))

        return start, end, is_range
    else:
        _start, _pos1 = validate_duration(start)

        _end, _pos2 = validate_duration(end)

        """
        If both start and end are  provided means that this
        is a range so, end can be smaller than start since it will be measure
        from the end of file towards start

        if _end > _start and end != -1:
            raise SlicerArgumentException(
                "Invalid range: end must be greater than start."
            )
        """

        # Range is True if both start and end are provide ie str, if not
        # provided type is int by default

        is_range = True if isinstance(start, str) and isinstance(end, str) else False

        start_ = _start if _pos1 == "sec" else _start * 60
        end_ = _end if _pos2 == "sec" else _end * 60

        return start_, end_, is_range


def validate_bitrate(bitrate) -> str:
    if isinstance(bitrate, (int, float)):
        return f"{bitrate}k"
    elif isinstance(bitrate, str):
        if bitrate.endswith("k") and bitrate[:-1].isnumeric():
            return bitrate
        else:
            return f"{"".join([x for x in bitrate if x.isnumeric() or x == '.'])}k"
