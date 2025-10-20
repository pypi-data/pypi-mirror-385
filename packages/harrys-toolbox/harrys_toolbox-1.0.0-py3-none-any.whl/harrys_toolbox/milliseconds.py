import time

_time_of_module_import = time.time()

def millis() -> int:
    """Returns the number of milliseconds since the module was imported, as an 
    integer.

    Returns:
        int: The number of milliseconds since the module was imported.
    """
    _milliseconds_since_start = int(time.time() - _time_of_module_import * 1000)

    return _milliseconds_since_start
