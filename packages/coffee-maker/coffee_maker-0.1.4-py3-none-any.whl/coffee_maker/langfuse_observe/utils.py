import inspect
from typing import List


def get_callers_modules() -> List[str]:
    """Gets the module names from the current call stack.

    Returns:
        List[str]: A list of module names or filenames from the call stack, starting from the current frame.
    """
    callers_modules = []
    for caller_frame_record in inspect.stack():
        calling_module = inspect.getmodule(caller_frame_record.frame)
        if calling_module:
            callers_modules.append(calling_module.__name__)
        else:
            callers_modules.append(caller_frame_record.filename)
    return callers_modules
