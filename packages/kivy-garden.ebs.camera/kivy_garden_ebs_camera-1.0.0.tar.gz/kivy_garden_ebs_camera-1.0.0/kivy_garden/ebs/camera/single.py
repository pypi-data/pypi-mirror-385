

from datetime import datetime

from kivy.clock import Clock
from kivy.properties import BooleanProperty, NumericProperty, ListProperty

from kivy.graphics import Color, Rectangle, Ellipse
from kivy.graphics.texture import Texture

from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.image import Image

from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.anchorlayout import AnchorLayout

from kivy_garden.ebs.core.labels import SelfScalingOneLineLabel


class RecordingIndicator(Widget):
    recording = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (140, 50)
        # blinking timer
        Clock.schedule_interval(self._blink, 0.5)
        self._visible = True

    def _blink(self, dt):
        self.canvas.after.clear()
        if not self.recording:
            return
        self._visible = not self._visible
        if self._visible:
            with self.canvas.after:
                Color(1, 0, 0, 1)   # red
                # Draw a small filled circle (10 px radius)
                Ellipse(pos=(10, self.y + 20), size=(20, 20))

    def on_pos(self, *args):
        # ensure the circle stays positioned relative to widget
        self._blink(0)


class CameraPreviewWidget(RelativeLayout):
    """
    Pure-Kivy widget for displaying a single camera stream.
    It doesn't fetch frames itself — expects external .update_frame() calls.
    """

    show_ts = BooleanProperty(True)
    show_key = BooleanProperty(True)
    show_path = BooleanProperty(True)
    show_card = BooleanProperty(True)
    show_crop = BooleanProperty(True)
    apply_crop = BooleanProperty(False)
    simplify = BooleanProperty(False)

    run_preview = BooleanProperty(False)
    errored = BooleanProperty(False)
    capturing = BooleanProperty(False)
    aspect_ratio = NumericProperty(4.0/3.0)
    effective_crop = ListProperty([0, 1, 0, 1])

    def __init__(self,
                 camera_key=None, connection_path=None, camera_card=None,
                 control_target=None,
                 **kwargs):
        super().__init__(**kwargs)

        self._updating_texture = False
        self._last_frame = None

        self.camera_key = camera_key or "Unknown"
        self.connection_path = connection_path or "N/A"
        self.camera_card = camera_card or "Unknown"
        self._control_target = control_target

        self._bottom_left_anchor = None
        self._top_right_stack = None
        self._bottom_right_stack = None

        self._alias_label = None
        self._pause_label = None
        self._timestamp_label = None
        self._connection_label = None
        self._card_label = None
        self._recording_indicator = None

        # Main image
        self.preview_image = Image(allow_stretch=True, keep_ratio=True)
        self.add_widget(self.preview_image)
        self._init_black_texture()

        # Overlay
        self._build_overlay()

        # Freeze shading overlay
        with self.canvas.after:
            self._freeze_color = Color(0, 0, 0, 0)
            self._freeze_rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self._update_overlay_geometry,
                  size=self._update_overlay_geometry)

        Clock.schedule_once(lambda dt: self._set_freeze_overlay(), 0)

    @property
    def control_target(self):
        return self._control_target

    def _init_black_texture(self):
        """Create and assign an initial black texture (for startup)."""
        from kivy.graphics.texture import Texture
        import numpy as np

        # Default resolution can be small; will stretch automatically
        w, h = 320, 240
        black_frame = np.zeros((h, w, 3), dtype=np.uint8)

        texture = Texture.create(size=(w, h), colorfmt='bgr')
        texture.blit_buffer(black_frame.tobytes(), colorfmt='bgr', bufferfmt='ubyte')
        self.preview_image.texture = texture

    def on_capturing(self, *_):
        self._recording_indicator.recording = self.capturing

    def on_show_ts(self, *_):
        if self.show_ts:
            if not self._timestamp_label.parent:
                self._bottom_right_stack.add_widget(self._timestamp_label)
        else:
            if self._timestamp_label.parent:
                self._bottom_right_stack.remove_widget(self._timestamp_label)

    def on_show_key(self, *_):
        if self.show_key:
            if not self._alias_label.parent:
                self._bottom_left_anchor.add_widget(self._alias_label)
        else:
            if self._alias_label.parent:
                self._bottom_left_anchor.remove_widget(self._alias_label)

    def on_show_path(self, *_):
        if self.show_path:
            if not self._connection_label.parent:
                self._top_right_stack.add_widget(self._connection_label)
        else:
            if self._connection_label.parent:
                self._top_right_stack.remove_widget(self._connection_label)

    def on_show_card(self, *_):
        if self.show_card:
            if not self._card_label.parent:
                self._top_right_stack.add_widget(self._card_label)
        else:
            if self._card_label.parent:
                self._top_right_stack.remove_widget(self._card_label)

    def on_simplify(self, *_):
        self.show_card = False
        if len(self.connection_path) <= 2:
            self.show_path = False

    def on_show_crop(self, *_):
        if self.control_target:
            self.control_target.preview_overlay_crop = self.show_crop

    def on_apply_crop(self, *_):
        if self.control_target:
            self.control_target.preview_apply_crop = self.apply_crop

    def on_run_preview(self, *_):
        self._set_freeze_overlay()

    def on_errored(self, *_):
        if self.errored:
            self._pause_label.text = "[error]"
            self.run_preview = False

    def _build_overlay(self):
        self._bottom_left_anchor = AnchorLayout(anchor_x='left', anchor_y='bottom', padding=10)
        self.add_widget(self._bottom_left_anchor)

        top_right_anchor = AnchorLayout(anchor_x='right', anchor_y='top', padding=10)
        self.add_widget(top_right_anchor)

        top_left_anchor = AnchorLayout(anchor_x='left', anchor_y='top', padding=10)
        self.add_widget(top_left_anchor)

        bottom_right_anchor = AnchorLayout(anchor_x='right', anchor_y='bottom', padding=10)
        self.add_widget(bottom_right_anchor)

        self._top_right_stack = StackLayout(orientation='tb-rl')
        top_right_anchor.add_widget(self._top_right_stack)

        self._bottom_right_stack = StackLayout(orientation='bt-rl')
        bottom_right_anchor.add_widget(self._bottom_right_stack)

        self._recording_indicator = RecordingIndicator(
            size_hint=(0.2, 0.2),
            size_hint_max_y=40,
        )
        top_left_anchor.add_widget(self._recording_indicator)

        if self.camera_key:
            self._alias_label = SelfScalingOneLineLabel(
                text=self.camera_key,
                color=(1, 1, 1, 0.9),
                halign='left',
                size_hint_x=0.5,
                size_hint_y=0.5,
                size_hint_max_y=100,
                font_size=90,
                bold=True,
            )
        self.on_show_key()

        if self.connection_path:
            self._connection_label = SelfScalingOneLineLabel(
                text=self.connection_path,
                color=(1, 1, 1, 0.9),
                halign='right',
                size_hint_x=0.8,
                size_hint_y=0.25,
                size_hint_max_y=48,
                font_size=42,
                bold=True,
            )
            self.on_show_path()

        if self.camera_card:
            self._card_label = SelfScalingOneLineLabel(
                text=self.camera_card,
                color=(1, 1, 1, 0.9),
                halign='right',
                size_hint_x=0.8,
                size_hint_y=0.20,
                size_hint_max_y=38,
                font_size=32,
            )
            self.on_show_card()

        self._pause_label = SelfScalingOneLineLabel(
            text="[paused]",
            color=(1, 1, 1, 0.9),
            halign='right',
            valign='center',
            size_hint_x=0.5,
            size_hint_y=0.25,
            size_hint_max_y=48,
            font_size=42,
        )

        # --- Timestamp label (bottom-right corner) ---
        self._timestamp_label = SelfScalingOneLineLabel(
            text="--:--:--.---",
            color=(1, 1, 1, 0.9),
            halign='right',
            valign='bottom',
            size_hint_x=0.5,
            size_hint_y=0.25,
            size_hint_max_y=48,
            font_size=42,
        )
        self.on_show_ts()

    def start_preview(self, *_):
        if self.run_preview:
            return
        self.run_preview = True

    def stop_preview(self, *_):
        if not self.run_preview:
            return
        self.run_preview = False

    def _set_freeze_overlay(self, *_):
        if not self.run_preview:
            self._freeze_color.a = 0.4
            if not self._pause_label.parent:
                self._bottom_right_stack.add_widget(self._pause_label)
        else:
            self._freeze_color.a = 0
            if self._pause_label.parent:
                self._bottom_right_stack.remove_widget(self._pause_label)

    def _update_overlay_geometry(self, *args):
        self._freeze_rect.pos = self.pos
        self._freeze_rect.size = self.size

    def update_frame(self, frame, timestamp=None):
        """Called externally to provide a new frame (NumPy array)."""
        if not self.run_preview:
            return
        if self._updating_texture:
            return

        self._last_frame = frame
        self._updating_texture = True

        if hasattr(self, "_timestamp_label"):
            if timestamp is None:
                timestamp = datetime.now()
            if isinstance(timestamp, (int, float)):
                ts_str = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S.%f")[:-3]
            elif isinstance(timestamp, datetime):
                ts_str = timestamp.strftime("%H:%M:%S.%f")[:-3]
            else:
                ts_str = str(timestamp)
            self._timestamp_label.text = ts_str

        Clock.schedule_once(self._do_update_texture, 0)

    def _do_update_texture(self, dt):
        frame = self._last_frame
        if frame is None:
            self._updating_texture = False
            return
        try:
            h, w = frame.shape[:2]
            colorfmt = "bgr" if frame.shape[2] == 3 else "bgra"
            buf = frame[::-1].tobytes()
            texture = Texture.create(size=(w, h), colorfmt=colorfmt)
            texture.blit_buffer(buf, colorfmt=colorfmt, bufferfmt="ubyte")
            self.preview_image.texture = texture
        finally:
            self._updating_texture = False
