

import sys
import traceback
from datetime import datetime
from json import dump, load
from typing import TypedDict


class ProgressObject(TypedDict):
    percent: float
    message: str


class LogFileObject(TypedDict):
    progress: ProgressObject | None
    main_errors: list[str]
    errors: list[str]


class Logger:

    log_file_path: str = None

    def __init__(self, log_file_path: str):
        self.log_file_path = log_file_path
        self._dump_log_file({
            "progress": None,
            "main_errors": [],
            "errors": []
        })

    def _dump_log_file(self, log_file_object: LogFileObject) -> None:
        with open(self.log_file_path, "w+", encoding='UTF-8') as f:
            dump(log_file_object, f)

    def _load_log_file(self) -> LogFileObject:
        try:
            with open(self.log_file_path, encoding='UTF-8') as f:
                return load(f)
        except Exception:
            return {
                "progress": None,
                "main_errors": [],
                "errors": []
            }

    def info(self, msg: str) -> None:
        self._log(msg, "INFO")

    def error(self, msg) -> None:
        self._log(msg, "ERROR")

        log_file = self._load_log_file()
        log_file["errors"].append(msg)
        self._dump_log_file(log_file)

    def main_error(self, msg) -> None:
        """
        Log an error message to the main output, it can be read by lab manager
        """
        self._log(f"{msg}", "ERROR")

        # Get the stack trace
        stack_trace = traceback.format_exc()

        log_file = self._load_log_file()
        log_file["main_errors"].append(msg)
        log_file["errors"].append(f"{msg}\n{stack_trace}")
        self._dump_log_file(log_file)

    def log_progress(self, msg: str, percent: int, log_in_console: bool = True) -> None:
        if log_in_console:
            self._log(f"{percent}% {msg}", "INFO")

        log_file = self._load_log_file()
        log_file["progress"] = {
            "percent": percent,
            "message": msg
        }
        self._dump_log_file(log_file)

    def _log(self, msg: str, type_: str) -> None:
        if msg.endswith("\n"):
            msg = msg[:-1]
        if type_ == "ERROR":
            sys.stderr.write(
                f"{type_} - {datetime.now().isoformat()} - {msg}")
        else:
            # get the date in UTC format
            print(f"{type_} - {datetime.now().isoformat()} - {msg}")
