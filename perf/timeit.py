from __future__ import absolute_import, print_function
import itertools
import subprocess
import sys
import timeit

import perf.text_runner


_DEFAULT_NPROCESS = 25
_DEFAULT_WARMUPS = 1
_DEFAULT_SAMPLES = 3
_MIN_TIME = 0.1
_MAX_TIME = 1.0


def _calibrate_timer(timer, verbose=0, stream=None):
    min_dt = _MIN_TIME * 0.90
    for i in range(0, 10):
        number = 10 ** i
        dt = timer.timeit(number)
        if verbose > 1:
            print("10^%s loops: %s" % (i, perf._format_timedelta(dt)), file=stream)
        if dt >= _MAX_TIME:
            i = max(i - 1, 1)
            number = 10 ** i
            break
        if dt >= min_dt:
            break
    if verbose > 1:
        print("calibration: use %s" % perf._format_number(number, 'loop'), file=stream)
    return number


def _main_common():
    runner = perf.text_runner.TextRunner()
    parser = runner.argparser
    parser.add_argument('-l', '--loops', type=int, default=0,
                        help='number of loops per sample (default: calibrate)')
    parser.add_argument('-s', '--setup', action='append', default=[],
                        help='setup statements')
    parser.add_argument('stmt', nargs='+',
                        help='executed statements')

    runner.parse_args()

    stmt = "\n".join(runner.args.stmt) or "pass"
    setup = "\n".join(runner.args.setup) or "pass"

    # Include the current directory, so that local imports work (sys.path
    # contains the directory of this script, rather than the current
    # directory)
    import os
    sys.path.insert(0, os.curdir)

    timer = timeit.Timer(stmt, setup, perf.perf_counter)
    if runner.args.loops == 0:
        stream = sys.stderr if runner.args.json else None
        try:
            runner.args.loops = _calibrate_timer(timer, runner.args.verbose, stream=stream)
        except:
            timer.print_exc()
            sys.exit(1)

    return (runner, timer)


def _prepare_args(runner, args):
    # replace ".../timeit.py" with "-m perf.timeit"
    args[1:2] = ['-m', 'perf.timeit']
    args.extend(("--loops", str(runner.args.loops)))
    for setup in runner.args.setup:
        args.extend(("--setup", setup))
    args.extend(runner.args.stmt)


def _main():
    runner, timer  = _main_common()
    runner.prepare_subprocess_args = _prepare_args

    def func(timer, loops):
        it = itertools.repeat(None, loops)
        return timer.inner(it, timer.timer) / loops

    loops = runner.args.loops
    runner.result.metadata['timeit_loops'] = perf._format_number(loops)
    try:
        runner.bench_sample_func(func, timer, loops)
    except:
        timer.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    _main()
