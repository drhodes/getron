'''
Stage 3: Diagnostics, Maintenance & Repair Specs
'''

from .err import Feat, Req


class DoctorDiagnostics(Feat):
    '''
    `getron doctor` performs a comprehensive system check including binary integrity,
    manifest validity, service unit status, permissions, and daemon IPC responsiveness.
    Outputs clear pass/fail status and actionable remediation advice.
    '''


class TargetedRepair(Feat):
    '''
    `getron repair` performs targeted fixes (restoring broken symlinks, re-writing service unit files,
    re-triggering daemon start) without performing full destruct-and-reinstall cycles.
    '''


class GarbageCollection(Feat):
    '''
    `getron gc` cleans up obsolete, non-active versions while preserving the active version
    and the most recent rollback target version.
    '''
