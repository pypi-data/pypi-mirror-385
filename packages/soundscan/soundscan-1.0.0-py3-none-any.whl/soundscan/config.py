import logging
from colorama import Fore, Style, init
init(autoreset=True)


class CustomFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: Fore.BLUE,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelno, Fore.WHITE)
        log_message = super().format(record)
        return f"{log_color}{log_message}{Style.RESET_ALL}"


# Set up logging
logger = logging.getLogger("enhanced_shazam")
handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter("- %(levelname)s - %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)
