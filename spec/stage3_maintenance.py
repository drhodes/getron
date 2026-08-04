'''
Stage 3: Diagnostics, Targeted Repair & Garbage Collection Specs
'''

from .err import Feat, Req


class DoctorInspectionReq(Req):
    '''
    `getron doctor` inspects host platform details, Getron CLI environment,
    active and installed Tetron versions, manifest integrity, active symlink validity,
    service unit configuration, and daemon IPC health.
    Emits structured pass/fail indicators and actionable recommendations.
    '''


class TargetedRepairReq(Req):
    '''
    `getron repair` performs non-destructive targeted repairs:
    restoring broken/missing `active` symlinks to the latest valid installed version,
    re-generating missing manifests, and repairing directory layout structure.
    '''


class GarbageCollectionReq(Req):
    '''
    `getron gc` safely removes obsolete installed versions from `<root>/versions/` while
    guaranteeing that the currently `active` version and the `rollback` target version
    are never removed.
    '''


class UninstallCommandFeat(Feat):
    '''
    `getron uninstall <version>` removes a specific installed version directory.
    Refuses to uninstall the currently active version unless forced or another version is active.
    '''
