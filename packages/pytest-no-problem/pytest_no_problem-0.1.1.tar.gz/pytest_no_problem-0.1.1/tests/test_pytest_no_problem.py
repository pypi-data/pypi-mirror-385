import pytest

from pytest_no_problem.no_problem_text import NO_PROBLEM_TEXT

pytest_plugins = "pytester"


def test_pytest_report_includes_text_if_all_passed(pytester: pytest.Pytester):
    pytester.makepyfile(
        """
        def test_pass():
            assert 1
        """,
    )

    result = pytester.runpytest()

    result.assert_outcomes(passed=1)
    assert result.ret == pytest.ExitCode.OK

    result.stdout.fnmatch_lines(NO_PROBLEM_TEXT.splitlines())


def test_pytest_report_does_not_include_text_if_failed(pytester: pytest.Pytester):
    pytester.makepyfile(
        """
        def test_fail():
            assert 0
        """,
    )

    result = pytester.runpytest()

    result.assert_outcomes(failed=1)
    assert result.ret == pytest.ExitCode.TESTS_FAILED

    # just test that the first non-empty line isn't in the output
    result.stdout.no_fnmatch_line(NO_PROBLEM_TEXT.splitlines()[1])
