import sys
from functools import wraps

from rushlib.output import print_red


def launch(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print_red(f"Error: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            print_red("\n\n操作已取消")
            sys.exit(1)

    return wrapper