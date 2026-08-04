'''
main spec
'''

from libspec import Spec
from . import app, stage1_bootstrap, stage2_installation, stage3_maintenance


class MainSpec(Spec):
    def modules(self):
        return [app, stage1_bootstrap, stage2_installation, stage3_maintenance]

