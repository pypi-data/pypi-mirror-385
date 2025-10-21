

from ebs.linuxnode.gui.kivy.core.basenode import BaseIoTNodeGui
from ebs.linuxnode.exim.mixin import LocalEximMixin

from .indicator import EximIndicator


class EximGuiMixin(BaseIoTNodeGui, LocalEximMixin):
    def __init__(self, *args, **kwargs):
        super(EximGuiMixin, self).__init__(*args, **kwargs)
        self._exim_indicator = None

    def signal_exim_action_start(self, tag, direction):
        if not self._exim_indicator:
            self._exim_indicator_show()
        self._exim_indicator.add_action((tag, direction))

    def signal_exim_action_done(self, tag, direction):
        if not self._exim_indicator:
            return
        if (tag, direction) in self._exim_indicator.actions.keys():
            self._exim_indicator.finish_action((tag, direction))

    @property
    def exim_indicator(self):
        if not self._exim_indicator:
            self._exim_indicator = EximIndicator()
        return self._exim_indicator

    def _exim_indicator_show(self):
        if not self.exim_indicator.parent:
            print("Trying to Show EXIM indicator")
            self._exim_indicator.bind(finished=lambda *_: self._exim_indicator_hide())
            self.gui_notification_row.add_widget(self._exim_indicator)
            self.gui_notification_update()

    def _exim_indicator_hide(self):
        if self._exim_indicator.parent:
            self._exim_indicator.parent.remove_widget(self._exim_indicator)
            self.gui_notification_update()
        self._exim_indicator = None
