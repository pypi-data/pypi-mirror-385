"""
Memory profiling utilities.

@author: Jakub Walczak
@organization: HappyRavenLabs
"""

__all__ = ["mem", "lmem"]
import linecache
import sys
import threading
import tracemalloc
from collections import defaultdict
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple

from .stats import Stats
from .writing import MemoryWriter


class mem:
    """
    Memory profiling utilities.

    Attributes
    ----------
    peak_memory_usage : Bytes
        Peak memory usage recorded during the profiling session.
    """

    _tracker: threading.local
    repeat: int
    out: Any
    usage: Stats

    def __init__(self, *, repeat: int = 1, out: Any = None):
        self._tracker = threading.local()
        self._tracker.running: set[Callable] = set()
        self.repeat = repeat
        self.out = out

    def __call__(self, func: Optional[Callable] = None) -> Callable:
        """Decorator for measuring memory usage of a function."""
        _mem_usages = []
        if self.repeat < 1:
            raise ValueError("Repeat must be at least 1.")

        @wraps(func)
        def wrapper(*args, **kwargs):
            if (
                hasattr(self._tracker, "running")
                and func in self._tracker.running
            ):
                return func(*args, **kwargs)
            try:
                self._tracker.running.add(func)
                result = None
                for _ in range(self.repeat):
                    tracemalloc.start()
                    result = func(*args, **kwargs)
                    _, peak = tracemalloc.get_traced_memory()
                    _mem_usages.append(peak)
                    tracemalloc.stop()
            finally:
                self._tracker.running.remove(func)
                self.usage = Stats(_mem_usages)
                MemoryWriter(self.out).with_func(func, *args, **kwargs).write(
                    _mem_usages
                )
            return result

        return wrapper

    def __enter__(self):
        if self.repeat > 1:
            raise ValueError(
                "Repeat must be 1 when used as a context manager."
            )
        tracemalloc.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        peak = tracemalloc.get_traced_memory()[1]
        tracemalloc.stop()
        self.usage = Stats([peak])
        MemoryWriter(output_target=self.out).write([peak])


class lmem:
    _tracker: threading.local
    out: Any
    usage: Dict[Tuple[str, int, str], Stats]

    def __init__(self, *, out: Any = None):
        self._tracker = threading.local()
        self._tracker.running: set[Callable] = set()
        self.out = out

    def __call__(
        self, func: Optional[Callable] = None, out: Any = None
    ) -> Callable:
        """Decorator for measuring memory usage of a function."""
        _mem_usages = []
        if func is None:
            raise ValueError("Function to be decorated must not be None.")

        @wraps(func)
        def wrapper(*args, **kwargs):
            _line_mem: Dict[int, List[float]] = defaultdict(list)
            _org_trace = sys.gettrace()
            _root_frame = sys._getframe(1)
            _root_file = _root_frame.f_code.co_filename
            _prev_line = None
            _prev_peak_mem = tracemalloc.get_traced_memory()[1]
            _last_line = None
            _with_line = _root_frame.f_lineno

            def _trace(frame, event: str, arg):
                nonlocal _prev_line, _prev_peak_mem, _last_line
                if event != "line":
                    return _trace

                current_file = frame.f_code.co_filename
                if current_file != _root_file:
                    return _trace
                _, peak = tracemalloc.get_traced_memory()
                if _prev_line is not None:
                    _line_mem[_prev_line].append(peak - _prev_peak_mem)

                filename = frame.f_code.co_filename
                lineno = frame.f_lineno
                _prev_line = (filename, lineno)
                _prev_peak_mem = peak
                return _trace

            if func in self._tracker.running:
                return func(*args, **kwargs)
            try:
                self._tracker.running.add(func)
                _root_frame.f_trace = _trace
                sys.settrace(_trace)
                tracemalloc.start()
                result = func(*args, **kwargs)
                _, peak = tracemalloc.get_traced_memory()
                _mem_usages.append(peak)
            finally:
                tracemalloc.stop()
                sys.settrace(_org_trace)
                self._tracker.running.remove(func)
                _line_mem = dict(
                    filter(
                        lambda item: item[0][1] != _with_line,
                        _line_mem.items(),
                    )
                )
                self.usage = {
                    (
                        linecache.getline(filename, lineno).strip(),
                        lineno,
                        filename,
                    ): Stats(usages)
                    for (filename, lineno), usages in _line_mem.items()
                }
                MemoryWriter(out).with_func(func, *args, **kwargs).write(
                    _mem_usages
                )
            return result

        return wrapper

    def __enter__(self):
        self._line_mem: Dict[int, List[float]] = defaultdict(list)
        self._org_trace = sys.gettrace()
        self._root_frame = sys._getframe(1)
        self._root_file = self._root_frame.f_code.co_filename
        self._prev_line = None
        self._prev_peak_mem = tracemalloc.get_traced_memory()[1]
        self._last_line = None
        self._with_line = self._root_frame.f_lineno

        def _trace(frame, event: str, arg):
            if event != "line":
                return _trace

            current_file = frame.f_code.co_filename
            if current_file != self._root_file:
                return _trace
            _, peak = tracemalloc.get_traced_memory()
            if self._prev_line is not None:
                self._line_mem[self._prev_line].append(
                    peak - self._prev_peak_mem
                )

            filename = frame.f_code.co_filename
            lineno = frame.f_lineno
            self._prev_line = (filename, lineno)
            self._prev_peak_mem = peak
            return _trace

        self._root_frame.f_trace = _trace
        sys.settrace(_trace)
        tracemalloc.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._prev_line is not None:
            peak = tracemalloc.get_traced_memory()[1]
            self._line_mem[self._prev_line].append(peak - self._prev_peak_mem)
        tracemalloc.stop()
        self._line_mem = dict(
            filter(
                lambda item: item[0][1] != self._with_line,
                self._line_mem.items(),
            )
        )
        self.usage = {
            (
                linecache.getline(filename, lineno).strip(),
                lineno,
                filename,
            ): Stats(usages)
            for (filename, lineno), usages in self._line_mem.items()
        }
        MemoryWriter(self.out).write(self._line_mem, root_file=self._root_file)
        sys.settrace(self._org_trace)
