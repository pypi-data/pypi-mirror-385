"""
Created in 2025 July

@author: Aron Gimesi (https://github.com/gimesia)
@contact: gimesiaron@gmail.com
"""

import time


class TicToc:
    """
    A simple timer class to measure elapsed time between events.
    Parameters
    ----------
    verbose : bool, optional
        If True, prints the elapsed time when `toc` is called. Default is False.
    Attributes
    ----------
    start_time : float or None
        The time when the timer was started. None if the timer has not been started.
    Methods
    -------
    tic()
        Start the timer.
    toc()
        Stop the timer and return the elapsed time. Raises a ValueError if the timer was not started.
    """

    def __init__(self, verbose=False):
        self.start_time = None
        self.verbose = verbose

    def tic(self):
        """Start the timer."""
        self.start_time = time.time()

    def toc(self):
        """Stop the timer and return elapsed time."""
        if self.start_time is None:
            raise ValueError("Timer not started. Call tic() first.")

        elapsed_time = time.time() - self.start_time
        if self.verbose:
            print(f"Elapsed time: {elapsed_time:.4f} seconds")

        return elapsed_time


@staticmethod
def timer(func):
    """Decorator to time a function execution."""

    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        print(f"{func.__name__} executed in {elapsed_time:.4f} seconds")
        return result

    return wrapper


# Example Usage:
if __name__ == "__main__":
    t = TicToc(True)
    t.tic()
    time.sleep(1.345)  # Example operation
    t.toc()

    @timer
    def example_function():
        time.sleep(1.234)

    example_function()
