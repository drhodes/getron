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
    Getron fetches release artifacts and checksums from GitHub Releases
    (`https://github.com/drhodes/tetron/releases/download/<version>/...`).
    Supports download verification via SHA-256 / SHA-512 checksum files.
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
