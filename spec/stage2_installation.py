'''
Stage 2: Versioned Staging, Manifests & Atomic Activation Specs
'''

from .err import Feat, Req


class StorageDirectoryLayoutReq(Req):
    '''
    Getron stores all installation artifacts in a dedicated root directory
    (default: `/usr/local/lib/tetron` or `$HOME/.local/share/tetron` if unprivileged).
    Directory structure:
      `<root>/versions/<version>/`  - Immutable installed versions
      `<root>/staging/`             - Temporary download & staging area
      `<root>/active`               - Symlink pointing to `<root>/versions/<version>`
      `<root>/rollback`             - Symlink pointing to previous known-good `<root>/versions/<version>`
      `<root>/state.json` (or `state.toml`) - Installation metadata & history
    '''


class ReleaseFetcherReq(Req):
    '''
    Getron fetches release artifacts directly from GitHub Releases (`ErikAllanKincaid/tetron`).
    When version is unspecified or set to `latest`, Getron resolves the latest release tag
    via GitHub API (`v0.9.3`). Maps platform names (e.g. Darwin to `macos`) dynamically.
    '''



class ManifestGeneratorReq(Req):
    '''
    Every installed version directory must contain a `manifest.toml` recording:
    `version`, `target`, `sha256`, `installed_at`, and IPC protocol compatibility version.
    '''


class AtomicSymlinkSwitchReq(Req):
    '''
    Version activation and rollback must switch the `<root>/active` pointer atomically
    using `ln -sfn` or temporary symlink replacement (`ln -s ... tmp && mv -f tmp active`).
    '''


class HealthCheckVerifierReq(Req):
    '''
    After activating a version, Getron verifies daemon responsiveness (IPC ping / status check).
    If verification fails, Getron automatically restores `<root>/active` to `<root>/rollback`
    and returns a descriptive error.
    '''


class VersionUseCommandFeat(Feat):
    '''
    `getron use <version>` switches the active version to an already installed version
    if present, verifying health and updating rollback pointers.
    '''


class AutomaticRollbackFeat(Feat):
    '''
    `getron rollback` explicitly restores the active symlink to the previous known-good version
    recorded in `<root>/rollback`.
    '''
