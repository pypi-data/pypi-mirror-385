

import os

from twisted.internet.defer import inlineCallbacks

from kivy.clock import Clock
from kivy.properties import DictProperty
from kivy.properties import BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout

from kivy_garden.ebs.core.image import StandardImage
from kivy_garden.ebs.core.labels import SelfScalingLabel
from kivy_garden.ebs.core.colors import ColorBoxLayout


class EximActionIndicator(RelativeLayout):
    finished = BooleanProperty(False)

    def __init__(self, container, key, **kwargs):
        self._tag, self._direction = key
        self._container = container
        kwargs.setdefault('pos_hint', {'left': 1})
        kwargs.setdefault('size_hint', (None, None))
        kwargs.setdefault('height', 50)
        kwargs.setdefault('width', 30)
        super(EximActionIndicator, self).__init__(**kwargs)
        self._create_core_container()
        self._create_icon()
        self._create_label()
        self.bind(finished=self._create_finished)

    def _create_core_container(self):
        self._core_container = BoxLayout(
            orientation='vertical',
            padding=0, spacing=0,
            size_hint=(1, 1),
        )
        self.add_widget(self._core_container)

    def _create_icon(self):
        if self._direction == 'export':
            imagefile = 'upload.png'
        else:
            imagefile = 'download.png'
        source = os.path.join(self._container.images_dir, imagefile)
        self._icon = StandardImage(source=source, size_hint=(1, 0.7))
        self._core_container.add_widget(self._icon)

    def _create_label(self):
        self._label = SelfScalingLabel(text=self._tag, size_hint=(1, 0.3))
        self._core_container.add_widget(self._label)

    def _create_finished(self, *_):
        source = os.path.join(self._container.images_dir, 'done.png')
        self._done = StandardImage(source=source, width=18, height=18,
                                   size_hint=(None, None),
                                   pos_hint={'right': 1, 'top': 1})
        self.add_widget(self._done)


class EximIndicator(ColorBoxLayout):
    actions = DictProperty({})
    finished = BooleanProperty(False)

    def __init__(self, **kwargs):
        kwargs.setdefault('bgcolor', (0x00 / 255., 0x00 / 255., 0x9f / 255., 0.5))
        kwargs.setdefault('pos_hint', {'left': 1})
        kwargs.setdefault('orientation', 'horizontal')
        kwargs.setdefault('padding', [0, 0, 0, 0])
        kwargs.setdefault('size_hint', (None, None))
        kwargs.setdefault('height', 50)
        kwargs.setdefault('spacing', 10)
        super(EximIndicator, self).__init__(**kwargs)
        self._min_timer = None
        self.bind(children=self._recalculate_size)
        self._min_elapsed = False
        self._create_base_children()
        self._duration = 30
        self._start_min_timer(self._duration)

    @property
    def images_dir(self):
        _root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
        return os.path.join(_root, 'images')

    def _recalculate_size(self, *_):
        self.width = sum([x.width for x in self.children]) + (10 * len(self.children))

    def _create_base_children(self):
        self._icon = StandardImage(
            source=os.path.join(self.images_dir, 'usbdrive.png'),
            size_hint=(None, 1), height=70)
        self._action_indicators = []
        self._icon.width = self._icon.norm_image_size[0]
        self.add_widget(self._icon)

    def _expire_lock(self):
        for key, action in self.actions.items():
            if not action.finished:
                return
        self.finished = True

    def _start_min_timer(self, period=None):
        if not period:
            period = self._duration
        self._min_timer = Clock.schedule_once(lambda *_: self._expire_lock(), period)

    def add_action(self, key):
        if key not in self.actions.keys():
            self.actions[key] = EximActionIndicator(container=self, key=key)
            self.add_widget(self.actions[key])

    def finish_action(self, key):
        self.actions[key].finished = True
        self._min_timer.cancel()
        self._start_min_timer()

    _context_durations = {
        'default': 10,
        'startup': 60,
        'hotplug': 8,
    }

    @inlineCallbacks
    def trigger(self, context):
        if context in self._context_durations.keys():
            self._duration = self._context_durations[context]
        else:
            self._duration = self._context_durations['default']
        yield super(EximIndicator, self).trigger(context)
