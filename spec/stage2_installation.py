'''
Stage 2: Versioned Staging & Atomic Activation Specs
'''

from .err import Feat, Req


class AtomicInstallationTransaction(Req):
    '''
    Installation and updates must be executed transactionally using a staging directory.
    Releases are fetched, verified via checksums, and unpacked before activation.
    If any step fails, existing installed versions remain completely untouched.
    '''


class ImmutableVersionLayout(Req):
    '''
    Each version of Tetron is stored in its own isolated directory (e.g. `versions/<ver>/`).
    Getron manages active version selection via atomic symlink updates (`active -> versions/<ver>`).
    '''


class AutomaticRollback(Feat):
    '''
    If daemon health checks fail upon activation of a new version, Getron must
    automatically roll back the `active` symlink and service to the previous known-good version.
    '''
