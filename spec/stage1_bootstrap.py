'''
Stage 1: Bootstrap, GitHub Origin & CLI Entrypoint Specs
'''

from .err import Feat, Req


class BootstrapScriptReq(Req):
    '''
    The bootstrap script (`install.sh`) must be a portable POSIX `/bin/sh` script.
    Its sole responsibility is downloading and installing the `getron` CLI script
    into a user/system PATH location (e.g. `$HOME/.local/bin` or `/usr/local/bin`).

    It must NOT install Tetron binaries or start system services directly.
    '''


class GitHubOriginFetcherReq(Req):
    '''
    Release assets and binary artifacts are fetched directly from GitHub repository releases
    (`https://github.com/drhodes/getron` or `https://github.com/drhodes/tetron`)
    rather than external custom domains.
    '''


class PlatformDiscoveryReq(Req):
    '''
    `getron` must discover host operating system (`uname -s`), CPU architecture (`uname -m`),
    and available service manager (`systemd`, `launchd`, `openrc`, `none`) using POSIX standard tools.
    '''


class SubcommandRouterFeat(Feat):
    '''
    `getron` parses CLI options and routes invocations to handler functions:
    `install`, `update`, `use`, `rollback`, `doctor`, `repair`, `gc`, `version`, `help`.
    '''


class InvalidSubcommandReq(Req):
    '''
    When invoked with an unknown command or invalid flags, `getron` must print a clear
    error message and usage summary to `stderr` and exit with status code 1.
    '''


class HelpOutputFeat(Feat):
    '''
    When invoked with `--help` or `help`, `getron` prints a clear, structured usage manual
    to `stdout` detailing all available commands and options.
    '''
