import logging
import os
import signal
from abc import abstractmethod
from collections import namedtuple
from contextlib import contextmanager
from subprocess import TimeoutExpired

import psutil

from turingarena.sandbox.exceptions import AlgorithmRuntimeError

logger = logging.getLogger(__name__)


class AlgorithmExecutable(namedtuple("AlgorithmExecutable", [
    "algorithm_dir",
    "language",
])):
    __slots__ = []

    @staticmethod
    def load(algorithm_dir):
        from turingarena.sandbox.languages.language import Language

        with open(os.path.join(algorithm_dir, "language.txt")) as f:
            language = Language.from_name(f.read().strip())

        return language.executable(
            algorithm_dir=algorithm_dir,
            language=language,
        )

    @staticmethod
    def _wait_or_send(process, which_signal):
        logger.debug(f"waiting for process...")
        try:
            process.wait(timeout=1.0)
        except TimeoutExpired:
            logger.warning(f"timeout expired! sending signal {which_signal}")
            process.send_signal(which_signal)

    @contextmanager
    def manage_process(self, process, get_stack_trace=None):
        logger.debug(f"starting process")
        with process:
            try:
                yield process
            finally:
                self._wait_or_send(process, signal.SIGQUIT)
                self._wait_or_send(process, signal.SIGKILL)

            if process.returncode != 0:
                logger.warning(f"process terminated with returncode {process.returncode}")
                raise AlgorithmRuntimeError(
                    f"invalid return code {process.returncode}",
                    get_stack_trace() if get_stack_trace else None,
                )

    def get_time_usage(self, process):
        time_usage = psutil.Process(process.pid).cpu_times().user
        logger.debug(f"time usage of PID {process.pid} == {time_usage}")
        return time_usage

    def get_memory_usage(self, process):
        memory_usage = psutil.Process(process.pid).memory_full_info().vms
        logger.debug(f"memory usage of PID {process.pid} == {memory_usage}")
        return memory_usage

    @abstractmethod
    def run(self, connection):
        pass
