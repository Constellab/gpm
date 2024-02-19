# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from datetime import datetime


class Logger:

    @classmethod
    def info(cls, msg: str):
        cls._log(msg, "INFO")

    @classmethod
    def error(cls, msg):
        cls._log(msg, "ERROR")

    @classmethod
    def _log(cls, msg: str, type_: str):
        # get the date in UTC format
        print(f"{type_} - {datetime.now().isoformat()} - {msg}")