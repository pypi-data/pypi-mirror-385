

from twisted.internet import reactor
from ebs.linuxnode.gui.kivy.core.basenode import BaseIoTNodeGui
from ebs.linuxnode.exim.mixin import LocalEximMixin
from ebs.linuxnode.gui.kivy.exim.mixin import EximGuiMixin


class ExampleNode(EximGuiMixin, BaseIoTNodeGui, LocalEximMixin):
    pass
