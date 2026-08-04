from libspec import Ctx, Feature, Requirement


class Err(Ctx):
    """
    It is important that error handling be done excellently.

    If a function can fail, then it needs to do so in the most elegant way
    possible. Error reporting, handling, exceptions and all aspects of failure
    must be taken to extreme. It should be possible to understand the program
    by reading the error messages.

    When an error occurs there should be a story about the failure at each step
    of the way. What went wrong and why.
    """


class PosixShBestPractices(Ctx):
    """
    Getron is implemented purely as a portable POSIX `/bin/sh` script.

    Standard POSIX `sh` rules and guidelines:
    1. Portability & Shell Standard:
       - Shebang: `#!/bin/sh`
       - Strict error control: `set -eu` (exit on error, unset variables treated as error).
       - Never use bashisms or non-standard syntax (e.g. `[[ ... ]]`, `<<<`, `array=(...)`, `function foo()`, `${var//search/replace}`).
       - Use standard test brackets `[ ... ]` and standard POSIX operator logic.
    2. Modularity & Clean Functions:
       - POSIX function definition syntax: `func_name() { ... }`.
       - Declare local-scope variables with `local` (or standard `_var` naming fallback if portability demands).
       - Keep functions focused and under 20 lines.
    3. Output & Signal Safety:
       - User messages on `stderr` (via `printf '%s\n' "message" >&2`).
       - Diagnostic / error formatting with clear status indicators and actionable user steps.
       - Clean cleanup handling via `trap 'cleanup' EXIT INT TERM`.
    4. Defensive File Operations & Atomic Transitions:
       - Always quote variable expansions to protect against spaces/special characters (`"$VAR"`).
       - Use temporary directories (`mktemp -d`) for downloads and staging operations.
       - Atomic directory replacement / symlink switches for version activation.
    """


class BoilerPlate(Ctx):
    """
    If you can see a way to reduce boiler plate, then do it.
    """


class FunctionLines(Ctx):
    """
    Try to keep functions under 20 lines.
    """


class Indentation(Ctx):
    """
    Try to keep indentation under 4 levels.
    """


class PreCondition(Ctx):
    """
    Functions should validate preconditions at their entry point.

    In POSIX sh, validate parameter counts, non-empty variables, file existence,
    and required tool availability (`command -v tool >/dev/null 2>&1`) before execution.
    Exit with descriptive error messages on failure.
    """


class GlobalMutableState(Ctx):
    """
    Broadly you should avoid global mutable state.
    """


class PostCondition(Ctx):
    """
    Before a function returns, it should verify postconditions to ensure
    invariant properties hold true.

    In POSIX sh, verify file creation, permissions, process execution status,
    and artifact checksums before completing operations.
    """


class DefensiveProgramming(PreCondition, PostCondition, GlobalMutableState):
    pass


class Refactor(BoilerPlate, FunctionLines, Indentation):
    """
    Always keep an eye out for ways to generalize a function if its utility
    might be helpful to other functions.

    Classes should be implemented in their own files with filename being the
    classname with correct naming convention.
    """


class Robustness(DefensiveProgramming, PosixShBestPractices):
    """
    Use dependency injection for system level objects and utilities for composability and ease of testing.
    Ensure external tool dependencies are checked before invoking commands.
    """


class Feat(Err, Refactor, Robustness, Feature):
    pass


class Req(Err, Refactor, Robustness, Requirement):
    pass

