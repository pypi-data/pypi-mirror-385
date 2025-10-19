from __future__ import annotations

from typing import TYPE_CHECKING

from pytest import Config, ExitCode

from .no_problem_text import NO_PROBLEM_TEXT

if TYPE_CHECKING:
    from _pytest.terminal import (
        TerminalReporter,  # pyright: ignore[reportPrivateImportUsage]
    )


def pytest_terminal_summary(
    terminalreporter: TerminalReporter,
    exitstatus: int,
    config: Config,  # noqa: ARG001
) -> None:
    """Add a section to terminal summary reporting."""
    if exitstatus == ExitCode.OK:
        terminalreporter.section(title="no problem")
        terminalreporter.write(NO_PROBLEM_TEXT)
