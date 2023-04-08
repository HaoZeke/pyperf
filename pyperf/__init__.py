from time import perf_counter

VERSION = (2, 6, 0)
__version__ = '.'.join(map(str, VERSION))

from pyperf._utils import python_implementation, python_has_jit  # noqa
from pyperf._metadata import format_metadata  # noqa
from pyperf._bench import Run, Benchmark, BenchmarkSuite, add_runs  # noqa
from pyperf._runner import Runner   # noqa
__all__ = [
    'perf_counter',
    'python_implementation',
    'python_has_jit',
    'format_metadata',
    'Run',
    'Benchmark',
    'BenchmarkSuite',
    'add_runs',
    'Runner',
]
