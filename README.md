# GETRON(1)

## NAME
getron - Tetron installation and lifecycle version manager

## SYNOPSIS
```sh
curl -fsSL https://raw.githubusercontent.com/drhodes/getron/main/install.sh | sh && getron install
```

## DESCRIPTION
getron is a POSIX /bin/sh version manager for Tetron. It handles installation, upgrades, version switching, rollback, diagnostics, and garbage collection.

Tetron releases are fetched directly from GitHub Releases (`drhodes/tetron`).

## COMMANDS
```
getron install [VERSION]
    Install specified version or latest release. Stages binary, writes manifest, and atomically updates active symlink.

getron update [--check]
    Check for or install available updates.

getron versions
    List all installed versions and indicate active selection.

getron use VERSION
    Switch active version to an installed VERSION. Reverts if health check fails.

getron rollback
    Revert active version to previous known-good version.

getron doctor
    Display diagnostic report detailing platform, installation paths, symlink integrity, and daemon status.

getron repair
    Rebuild missing or corrupted active symlinks without data loss.

getron gc
    Remove unreferenced version directories, preserving active and rollback targets.

getron uninstall VERSION
    Delete an installed VERSION directory. Refuses deletion if VERSION is active.

getron version
    Print getron version string.
```

## FILES
```
$HOME/.local/bin/getron
    Default user binary location for getron executable.

$HOME/.local/share/tetron/
/usr/local/lib/tetron/
    Root installation directory (user / root).

<root>/versions/<VERSION>/
    Immutable version directories.

<root>/active
    Symlink pointing to current active version directory.

<root>/rollback
    Symlink pointing to previous known-good version directory.
```

## ENVIRONMENT
```
GETRON_ROOT
    Override root installation directory.

GETRON_INSTALL_DIR
    Override binary install destination for install.sh (default: $HOME/.local/bin).
```
