import os, sys

class Colors:
    ENABLED = sys.stdout.isatty() and (os.name != "nt" or "ANSICON" in os.environ or "WT_SESSION" in os.environ)

    RESET="\033[0m"; BOLD="\033[1m"; UNDERLINE="\033[4m"
    RED="\033[31m"; GREEN="\033[32m"; YELLOW="\033[33m"
    BLUE="\033[34m"; MAGENTA="\033[35m"; CYAN="\033[36m"; WHITE="\033[37m"

    @staticmethod
    def c(text, color):
        if not Colors.ENABLED: return str(text)
        return f"{color}{text}{Colors.RESET}"