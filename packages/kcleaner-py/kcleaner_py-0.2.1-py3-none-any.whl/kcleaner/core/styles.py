class SmartStyles:
    """ANSI styles for output display"""

    INFO = "\033[94m[i]\033[0m"
    WARN = "\033[93m[!]\033[0m"
    ERR = "\033[91m[x]\033[0m"
    EXP = "\033[95m[⁉️]\033[0m"  # For exceptios
    EPH = "\033[1m"  # Bold for emphasis
    OK = "\033[92m[✓]\033[0m"
    RESET = "\033[0m"
