

from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy_garden.ebs.core.colors import ColorBoxLayout


class CaptureProgressOverlay(RelativeLayout):
    progress = NumericProperty(0)
    max_progress = NumericProperty(1)
    current_step = StringProperty("waiting")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Center container (progress bar + label)
        self._container = ColorBoxLayout(
            bgcolor=(0, 0, 0, 0.4),
            bgradius=[dp(8)],
            orientation='vertical',
            size_hint=(0.6, None),
            height=dp(80),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            spacing=dp(5)
        )

        self._label = Label(
            text="Waiting ...",
            size_hint_y=None,
            height=dp(30),
            halign="center",
            valign="middle",
            color=(1, 1, 1, 1)
        )

        self._progressbar = ProgressBar(
            max=self.max_progress,
            value=self.progress,
            size_hint_y=None,
            height=dp(20)
        )

        self._container.add_widget(self._label)
        self._container.add_widget(self._progressbar)
        self.add_widget(self._container)

        self.bind(progress=self._update_progress)
        self.bind(max_progress=self._update_progress)
        self.bind(current_step=self._update_label)

    def _update_rect(self, *args):
        self._rect.size = self.size
        self._rect.pos = self.pos

    def _update_progress(self, *args):
        self._progressbar.max = self.max_progress
        self._progressbar.value = self.progress

    def _update_label(self, *args):
        self._label.text = f"Capturing : {self.current_step}"

    # ---- API: call this from on_progress ----
    def update_from_progress(self, progress_dict):
        """
        Update the overlay based on a progress dict:
        {'key': 'A', 'max': 5, 'done': 2, 'current': 'crop'}
        """
        self.max_progress = progress_dict.get("max", 1)
        self.progress = progress_dict.get("done", 0)
        self.current_step = progress_dict.get("current", "")
