import numpy as np


class DuplicateTimesWarning(UserWarning):
    """For when duplicate times are found in a file."""
    def __init__(self, times):
        self.times = times
    
    def _msg(self, times) -> str:
        m = f"Duplicate timestamps found: {times[np.where(times.duplicated())[0]]}. That's bad."
        return m
    
    def __str__(self):
        return self._msg(self.times)
    