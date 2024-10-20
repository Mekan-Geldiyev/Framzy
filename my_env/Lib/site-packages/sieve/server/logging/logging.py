"""
This module defines how we handle logging in Sieve.

We have both an internal logger and external logger,
both of which we route differently to Sieve. We also
define custom stdout and stderr classes to capture
the output of the user code and route it to the
external logger.
"""

import json
import sys
import datetime
from io import StringIO

import logging
from typing import Literal


class SieveInternalLogger:
    """
    Drop-in replacement for the logging module that routes all logs to stdout.
    """

    def __init__(self):
        self.loglevel = "DEBUG"

    def setLevel(self, level):
        self.loglevel = level

    def info(self, message):
        sys.stdout.write(f"<SIEVE_INTERNAL> {message} </SIEVE_INTERNAL>\n")

    def profile(
        self,
        message: str,
        metadata: dict = None,
        period: Literal["start", "end"] = "start",
    ):
        out = metadata or {}
        out["message"] = message
        out["type"] = "profile"
        out["period"] = period
        out["timestamp"] = metadata.get("timestamp") or datetime.datetime.now(
            datetime.timezone.utc
        ).strftime("%Y-%m-%d %H:%M:%S,%f")
        sys.stdout.write(f"<SIEVE_INTERNAL> {json.dumps(out)} </SIEVE_INTERNAL>\n")

    def debug(self, message):
        sys.stdout.write(f"<SIEVE_INTERNAL> {message} </SIEVE_INTERNAL>\n")


sieve_internal_logger = SieveInternalLogger()


def get_sieve_internal_logger():
    return sieve_internal_logger


class CustomStdOut(StringIO):
    """
    This class defines a custom stderr class that we use to capture the output of the user code and
    internal Sieve logs, which are formatted differently.

    We use this to annotate user outputs before they hit stdout so they can be stored
    and viewed later.
    """

    def __init__(self, metadata={}, runner=None, *args, **kwargs):
        self.metadata = metadata
        super().__init__(*args, **kwargs)
        self.runner = runner
        self._stdout = sys.stdout
        self.buffer = []

    def write(self, s):
        if "<SIEVE_INTERNAL>" in s and "</SIEVE_INTERNAL>" in s:
            self._stdout.write(s)
            return
        if "\n" not in s:
            self.buffer.append(s)
            return
        if len(self.buffer) > 0:
            s = "".join(self.buffer) + s
            self.buffer = []
        formatted = {
            "type": "stdout",
            "message": s,
            "metadata": self.metadata,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime(
                "%Y-%m-%d %H:%M:%S,%f"
            ),
        }
        if self.runner:
            self.runner.setup_logs.append(formatted)
        formatted_string = json.dumps(formatted)
        if "<sieve>" in formatted_string or "</sieve>" in formatted_string:
            formatted_string = formatted_string.replace("<sieve>", "").replace(
                "</sieve>", ""
            )
        sieve_decorated_string = f"<sieve>{formatted_string}</sieve>\n"
        self._stdout.write(sieve_decorated_string)


class CustomStdErr(StringIO):
    """
    This class defines a custom stderr class that we use to capture the output of the user code and
    internal Sieve logs, which are formatted differently.

    We use this to annotate user outputs before they hit stderr so they can be stored
    and viewed later.
    """

    def __init__(self, metadata={}, runner=None, *args, **kwargs):
        self.metadata = metadata
        self.runner = runner
        super().__init__(*args, **kwargs)
        self._stderr = sys.stderr
        self.buffer = []

    def write(self, s):
        if "<SIEVE_INTERNAL>" in s and "</SIEVE_INTERNAL>" in s:
            self._stderr.write(s)
            return
        if "\n" not in s:
            self.buffer.append(s)
            return
        if len(self.buffer) > 0:
            s = "".join(self.buffer) + s
            self.buffer = []
        formatted = {
            "type": "stderr",
            "message": s,
            "metadata": self.metadata,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime(
                "%Y-%m-%d %H:%M:%S,%f"
            ),
        }
        if self.runner:
            self.runner.setup_logs.append(formatted)
        formatted_string = json.dumps(formatted)
        if "<sieve>" in formatted_string or "</sieve>" in formatted_string:
            formatted_string = formatted_string.replace("<sieve>", "").replace(
                "</sieve>", ""
            )
        sieve_decorated_string = f"<sieve>{formatted_string}</sieve>\n"
        self._stderr.write(sieve_decorated_string)


class StdoutCapturing(list):
    def __init__(self, metadata={}, runner=None):
        self.metadata = metadata
        self.runner = runner
        super().__init__()

    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = CustomStdOut(self.metadata, runner=self.runner)
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio  # free up some memory
        sys.stdout = self._stdout


class StderrCapturing(list):
    def __init__(self, metadata={}, runner=None):
        self.metadata = metadata
        self.runner = runner
        super().__init__()

    def __enter__(self):
        self._stderr = sys.stderr
        sys.stderr = self._stringio = CustomStdErr(self.metadata, runner=self.runner)
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio  # free up some memory
        sys.stderr = self._stderr
