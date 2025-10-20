import os
import sys

class Colors:
    """Simple ANSI color utility with auto-disable on unsupported terminals."""
    
    ENABLED = sys.stdout.isatty() and os.name != 'nt' or 'ANSICON' in os.environ

    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    @staticmethod
    def colorize(text, color):
        if not Colors.ENABLED:
            return text
        return f"{color}{text}{Colors.RESET}"
