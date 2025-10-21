

from ebs.linuxnode.core.log import NodeLoggingMixin
from ebs.linuxnode.core.busy import NodeBusyMixin
from ebs.linuxnode.core.shell import BaseShellMixin
from ebs.linuxnode.core.config import ElementSpec, ItemSpec

from .local import LocalEximManager


class LocalEximMixin(BaseShellMixin, NodeBusyMixin, NodeLoggingMixin):
    def __init__(self, *args, **kwargs):
        super(LocalEximMixin, self).__init__(*args, **kwargs)
        self._exim = None

    def signal_exim_action_start(self, tag, direction):
        pass

    def signal_exim_action_done(self, tag, direction):
        pass

    @property
    def exim(self):
        if not self._exim:
            self._exim = LocalEximManager(self)
        return self._exim

    def exim_install(self):
        super(LocalEximMixin, self).exim_install()

    def install(self):
        super(LocalEximMixin, self).install()
        _elements = {
            'exim_local_enabled': ElementSpec('exim', 'local_enabled', ItemSpec(bool, fallback=True)),
            'exim_local_mountpoint': ElementSpec('exim', 'local_mountpoint', ItemSpec(fallback='/exim')),
            'exim_startup_wait': ElementSpec('exim', 'startup_wait', ItemSpec(int, fallback=20)),
        }
        for name, spec in _elements.items():
            self.config.register_element(name, spec)

        self.exim.install()
        self.exim_install()

    def start(self):
        super(LocalEximMixin, self).start()
        self.reactor.callLater(self.config.exim_startup_wait, self.exim.trigger, 'startup')
