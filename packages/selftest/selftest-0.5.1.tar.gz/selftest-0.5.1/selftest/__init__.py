## begin license ##
#
# "selftest": a simpler test runner for python
#
# Copyright (C) 2021-2023 Seecr (Seek You Too B.V.) https://seecr.nl
#
# This file is part of "selftest"
#
# "selftest" is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# "selftest" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "selftest".  If not, see <http://www.gnu.org/licenses/>.
#
## end license ##


"""
    The structure of selftests for bootstrapping.
    ---------------------------------------------
    * tester.py contains the main Tester without any hooks, this module tests itself using a
      separate Tester called self_test. We reuse self_test to incrementally run the tests for
      the hooks.
    * self_test contains one hook: operator, in order to make testing easier. However, a
      small mistake in operator might cause all tests to fail since Tester and operator
      mutually depend on each other.
    * After all hooks have been tested, we assemble the final root Tester and tests if
      all hooks work properly.
    * Run tests for selftest itself by:
       $ python3 -c "import selftest" selftest.selftest
    * Integration tests are run with a partially initialized __init__.py, but it works
    * Finally we test the setup

"""


import os


from .tester import Tester, self_test


@self_test
def assert_stats():
    assert {"found": 21, "run": 20} == self_test.stats, self_test.stats


from .levels import levels_hook, levels_test

levels_test(self_test)

from .prrint import prrint_test

prrint_test(self_test)

from .filter import filter_hook, filter_test

filter_test(self_test)

from .wildcard import wildcard_hook, wildcard_test

wildcard_test(self_test)

from .binder import binder_hook, binder_test

binder_test(self_test)

from .operators import operators_hook, operators_test

operators_test(self_test)

from .fixtures import fixtures_hook, fixtures_test, std_fixtures

fixtures_test(self_test)

from .asyncer import async_hook, async_test

async_test(self_test)

from .diffs import diff_hook, diff_test

diff_test(self_test)


@self_test
def check_stats():
    self_test.eq({"found": 161, "run": 135}, self_test.stats)


def assemble_root_runner(**options):
    return Tester(
        # order of hook matters, processed from right to left
        hooks=[
            operators_hook,
            async_hook,
            fixtures_hook,
            diff_hook,
            levels_hook,
            wildcard_hook,
            binder_hook,
            filter_hook,
        ],
        fixtures=std_fixtures,
        **options,
    )


def root_tester_assembly_test(test):
    """only test if the root tester is assembled with all hooks"""

    N = [0]

    # operators_hook
    test.eq(1, 1)
    test.isinstance({}, dict)
    test.endswith("aap", "ap")

    # fixtures hook
    @test.fixture
    def forty_two():
        yield 42

    @test
    def is_forty_two(forty_two):
        assert forty_two == 42
        N[0] += 1

    with test.forty_two as contextmanager:
        assert contextmanager == 42

    # standard fixtures
    with test.tmp_path as p:
        test.truth(p.exists())
    with test.stdout as e:
        print("one")
        assert e.getvalue() == "one\n"
    with test.stderr as e:
        import sys

        print("two", file=sys.stderr)
        assert e.getvalue() == "two\n"

    # binding hook
    class A:
        a = 42

        @test(bind=True)
        def bind():
            assert a == 42
            N[0] += 1

    # wildcard hook
    test.eq(test.any(int), 42)

    # levels hook
    from .levels import UNIT

    assert test.level == 40, test.level
    assert test.threshold == 30, test.threshold
    with test.child(threshold=UNIT) as tst:

        @tst.performance
        def performance_test():
            assert "not" == "executed"

        @tst.critical
        def critical_test():
            assert 1 == 1
            N[0] += 1

        assert {"found": 2, "run": 1} == tst.stats, tst.stats

    # async hook (elaborate on nested stuff)
    @test.fixture
    async def nine():
        yield [
            "borg 1",
            "borg 2",
            "borg 3",
            "borg 4",
            "borg 5",
            "borg 6",
            "Annika Hansen",
            "borg 8",
            "borg 9",
        ]

    @test.fixture
    async def seven_of_nine(nine):
        yield nine[7 - 1]

    @test
    async def the_9(nine):
        assert len(nine) == 9
        N[0] += 1

    @test
    async def is_seven_of_nine(seven_of_nine):
        assert seven_of_nine == "Annika Hansen"
        N[0] += 1

    assert N[0] == 5, N
    assert dict(found=6, run=5) == test.stats, test.stats

    # diff hook
    try:
        test.eq(1, 2, diff=test.diff)
    except AssertionError as e:
        assert str(e) == "\n- 1\n+ 2"
    try:
        test.eq(1, 2, diff=test.diff2)
    except AssertionError as e:
        assert str(e) == "\n- 1\n+ 2"

    # filter hook
    @test(filter="aa")
    def moon():
        test.fail()

    r = [0]

    @test(filter="aa")
    def maan():
        r[0] = 1

    assert r == [1]


testers = {}  # initial, for more testing


def basic_config(**options):
    # raise Exception
    CR = '\n'
    assert None not in testers, f"Root {testers[None]}{CR} already configured."
    testers[None] = assemble_root_runner(**options)


def get_tester(name=None):
    if None not in testers:
        testers[None] = assemble_root_runner()
    if name in testers:
        return testers[name]
    tester = testers[None]
    for namepart in name.split("."):
        tester = tester.getChild(namepart)
        testers[tester._name] = tester
    return tester


@self_test
def set_root_opts():
    basic_config(filter="aap")
    root = get_tester()
    self_test.eq(
        {"filter", "fixtures", "hooks", "keep", "run", "subprocess"},
        set(root._options.keys()),
    )
    self_test.eq("aap", root._options["filter"])


@self_test
def get_root_tester():
    root = get_tester()
    assert isinstance(root, Tester)
    root1 = get_tester()
    assert root1 is root


@self_test
def get_sub_tester():
    root = get_tester()
    mymodule = get_tester("my.module")
    assert mymodule._name == "my.module"
    my = get_tester("my")
    assert my._name == "my"
    assert my._parent is root
    assert mymodule._parent is my
    mymodule1 = get_tester("my.module")
    assert mymodule1 is mymodule


testers.clear()


@self_test
def run_integration_tests():
    root_tester_assembly_test(assemble_root_runner())
    from .integrationtests import integration_test

    integration_test(assemble_root_runner().integration)


testers.clear()


@self_test
def setup_correct():
    import tempfile
    import pathlib
    import setuptools

    with tempfile.TemporaryDirectory() as p:
        tmp = pathlib.Path(p)
        selftest_dev_dir = pathlib.Path(__file__).parent.resolve().parent
        if not (selftest_dev_dir / "bin/selftest").exists():
            # Not dev dir
            return
        import subprocess

        version_process = subprocess.run(
            ["python3", "setup.py", "--version"],
            capture_output=True,
            text=True,
            cwd=str(selftest_dev_dir),
        )
        version = version_process.stdout.strip()
        result = subprocess.run(
            ["python3", "setup.py", "sdist", "--dist-dir", str(tmp)],
            capture_output=True,
            cwd=str(selftest_dev_dir),
        )

        from tarfile import open

        tf = open(name=tmp / f"selftest-{version}.tar.gz", mode="r:gz")
        self_test.eq(
            [
                f"selftest-{version}",
                f"selftest-{version}/LICENSE",
                f"selftest-{version}/MANIFEST.in",
                f"selftest-{version}/PKG-INFO",
                f"selftest-{version}/README.rst",
                f"selftest-{version}/bin",
                f"selftest-{version}/bin/selftest",
                f"selftest-{version}/selftest",
                f"selftest-{version}/selftest.egg-info",
                f"selftest-{version}/selftest.egg-info/PKG-INFO",
                f"selftest-{version}/selftest.egg-info/SOURCES.txt",
                f"selftest-{version}/selftest.egg-info/dependency_links.txt",
                f"selftest-{version}/selftest.egg-info/top_level.txt",
                f"selftest-{version}/selftest/__init__.py",
                f"selftest-{version}/selftest/__main__.py",
                f"selftest-{version}/selftest/asyncer.py",
                f"selftest-{version}/selftest/binder.py",
                f"selftest-{version}/selftest/diffs.py",
                f"selftest-{version}/selftest/filter.py",
                f"selftest-{version}/selftest/fixtures.py",
                f"selftest-{version}/selftest/integrationtests.py",
                f"selftest-{version}/selftest/levels.py",
                f"selftest-{version}/selftest/mocks.py",
                f"selftest-{version}/selftest/operators.py",
                f"selftest-{version}/selftest/prrint.py",
                f"selftest-{version}/selftest/tester.py",
                f"selftest-{version}/selftest/tests",
                f"selftest-{version}/selftest/tests/__init__.py",
                f"selftest-{version}/selftest/tests/sub_module_fail.py",
                f"selftest-{version}/selftest/tests/sub_module_ok.py",
                f"selftest-{version}/selftest/tests/temporary_class_namespace.py",
                f"selftest-{version}/selftest/tests/tryout.py",
                f"selftest-{version}/selftest/tests/tryout2.py",
                f"selftest-{version}/selftest/utils.py",
                f"selftest-{version}/selftest/wildcard.py",
                f"selftest-{version}/setup.cfg",
                f"selftest-{version}/setup.py",
            ],
            sorted(tf.getnames()),
            diff=lambda a, b: set(a).symmetric_difference(set(b)),
        )
        tf.close()


"""
We put these last, as printing any debug/trace messages anywhere in the code causes this
to fail.
"""

with self_test.child(hooks=[fixtures_hook], fixtures=std_fixtures) as self_test2:

    @self_test2
    def main_without_args(stdout):
        os.system("PYTHONPATH=. python3 selftest")
        assert "Usage: selftest [options] module" in stdout.getvalue()

    @self_test2
    def main_without_help(stdout):
        os.system("PYTHONPATH=. python3 selftest --help")
        s = stdout.getvalue()
        assert "Usage: selftest [options] module" in s
        assert "-h, --help            show this help message and exit" in s
        assert "-f FILTER, --filter=FILTER" in s
        assert "only run tests whose qualified name contains FILTER" in s
        assert "-t THRESHOLD, --threshold=THRESHOLD" in s
        assert "only run tests whose level is >= THRESHOLD" in s

    @self_test2
    def main_test(stderr, stdout):
        import os

        os.system("PYTHONPATH=. python3 selftest selftest/tests/tryout.py")
        e = stderr.getvalue()
        s = stdout.getvalue()
        assert "" == s, s
        loglines = [l for l in e.splitlines() if not '^^^^' in l]
        assert "importing selftest.tests.tryout" in loglines[0], loglines[0]
        assert loglines[1].startswith(
            "\033[1mTEST\033[0m:\033[1mUNIT:selftest.tests.tryout.one_simple_test\033[0m:"
        ), loglines[1]
        assert loglines[1].endswith("/selftest/selftest/tests/tryout.py:29"), loglines[ 1 ]
        assert loglines[2].startswith(
            "\033[1mTEST\033[0m:\033[1mINTEGRATION:selftest.tests.tryout.one_more_test\033[0m:"
        ), loglines[2]
        assert loglines[2].endswith("/selftest/selftest/tests/tryout.py:34"), loglines[ 2 ]
        assert " 31  \t    test.eq(1, 1)" == loglines[3]
        assert " 32  \t" == loglines[4]
        assert " 33  \t" == loglines[5]
        assert " 34  \t@test.integration" == loglines[6]
        assert " 35  \tasync def one_more_test():" == loglines[7]
        assert ' 36  ->\t    assert 1 == 2, "one is not two"' == loglines[8]
        assert " 37  \t    test.eq(1, 2)" == loglines[9]
        assert "[EOF]" == loglines[10]
        assert "Traceback (most recent call last):" in loglines[11]
        # some stuff in between we can't get rid off
        #
        import sys
        assert "in <module>" in loglines[-5]
        assert "selftest/tests/tryout.py" in loglines[-5]
        if sys.version_info.minor < 11:
            assert "async def one_more_test():" in loglines[-4], '\n'.join(loglines[-5:])
        assert "in one_more_test" in loglines[-3]
        assert "selftest/tests/tryout.py" in loglines[-3]
        assert "assert 1 == 2" in loglines[-2]
        assert "AssertionError: one is not two" in loglines[-1], loglines[-1]
        expected_length = 21
        if sys.version_info.minor < 11:
            expected_length = 23
        assert expected_length == len(loglines), f'{len(loglines)} ' + "\n".join(repr(l) for l in loglines)

    # @self_test2
    def main_with_selftests(stdout, stderr):
        os.system("PYTHONPATH=. python3 selftest selftest.selftest")
        lns = stdout.getvalue().splitlines()
        assert ["Usage: selftest [options] module", ""] == lns, lns
        lns = stderr.getvalue().splitlines()
        assert len(lns) == 144, len(lns)  # number of logged tests, sort of

    def assert_output(stdout, stderr):
        o = stdout.getvalue()
        self_test2.eq("", o)
        lines = stderr.getvalue().splitlines()
        self_test2.startswith(
            lines[0],
            "\033[1mTEST\033[0m:\033[1mimporting selftest.tests.tryout2\033[0m:",
        )
        self_test2.startswith(
            lines[1],
            "\033[1mTEST\033[0m:\033[1mUNIT:selftest.tests.tryout2.one_simple_test\033[0m:",
        )
        self_test2.startswith(
            lines[2],
            "\033[1mTEST\033[0m:\033[1mINTEGRATION:selftest.tests.tryout2.one_integration_test\033[0m:",
        )
        self_test2.startswith(
            lines[3], "\033[1mTEST\033[0m:\033[1mstats: found: 3, run: 2\033[0m:"
        )

    @self_test2
    def main_via_bin_script_with_selftest_on_path(stdout, stderr):
        os.system(f"PATH=./bin:$PATH selftest selftest/tests/tryout2.py")
        assert_output(stdout, stderr)

    @self_test2
    def main_via_bin_script_in_cur_dir(stdout, stderr):
        os.system(f"(cd bin; ./selftest selftest/tests/tryout2.py)")
        assert_output(stdout, stderr)

    @self_test2
    def main_with_filter(stdout, stderr):
        os.system(
            "PYTHONPATH=. python3 selftest selftest/tests/tryout2.py --filter one_simple"
        )
        o = stdout.getvalue()
        assert "" == o, o
        e = stderr.getvalue()
        assert "one_simple_test" in e, e
        assert "one_integration_test" not in e, e
        assert "one_performance_test" not in e
        assert "found: 3, run: 1" in e, e

    @self_test2
    def main_with_level_unit(stdout, stderr):
        os.system(
            "PYTHONPATH=. python3 selftest selftest/tests/tryout2.py --threshold unit"
        )
        o = stdout.getvalue()
        assert "" == o, o
        e = stderr.getvalue()
        assert "one_simple_test" in e, e
        assert "one_integration_test" not in e, e
        assert "one_performance_test" not in e
        assert "found: 3, run: 1" in e, e

    @self_test2
    def main_with_level_integration(stdout, stderr):
        os.system(
            "PYTHONPATH=. python3 selftest selftest/tests/tryout2.py --threshold integration"
        )
        o = stdout.getvalue()
        assert "" == o, o
        e = stderr.getvalue()
        assert "one_simple_test" in e, e
        assert "one_integration_test" in e, e
        assert "one_performance_test" not in e
        assert "found: 3, run: 2" in e, e
