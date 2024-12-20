

from datetime import datetime
import sys


class Logger:

    @classmethod
    def info(cls, msg: str) -> None:
        cls._log(msg, "INFO")

    @classmethod
    def error(cls, msg)-> None:
        cls._log(msg, "ERROR")
        
    @classmethod
    def log_progress(cls, msg: str, percent: int)-> None:
        cls._log(f"[PROGRESS]{percent}%[PROGRESS] {msg}", "INFO")
        

    @classmethod
    def _log(cls, msg: str, type_: str)-> None:
        if type_ == "ERROR":
            sys.stderr.write(
                f"{type_} - {datetime.now().isoformat()} - {msg}")
        else:
            # get the date in UTC format
            print(f"{type_} - {datetime.now().isoformat()} - {msg}")

        #
