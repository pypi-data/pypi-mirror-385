

from kivy_garden.ebs.core.labels import ColorLabel
from kivy.clock import Clock
from kivy.properties import NumericProperty, ListProperty, DictProperty
from kivy.properties import BooleanProperty

from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout

from .single import CameraPreviewWidget


class MultiCameraPreviewWidget(ScrollView):
    """
    Pure Kivy container for multiple CameraPreviewWidget instances.
     - Automatically reflows based on available width.
     - Keeps 4:3 aspect ratio for camera previews.
     - Expands previews proportionally when more space is available.
     - Scrolls vertically only when needed.
    """

    spacing = NumericProperty(8)
    padding = NumericProperty(8)

    desired_width = NumericProperty(320)

    show_ts = BooleanProperty(True)
    show_key = BooleanProperty(True)
    show_path = BooleanProperty(True)
    show_card = BooleanProperty(True)
    show_crop = BooleanProperty(True)
    apply_crop = BooleanProperty(False)
    simplify = BooleanProperty(False)

    run_preview = BooleanProperty(False)
    enabled_previews = ListProperty([])
    camera_widgets = DictProperty({})

    def __init__(self, control_target=None, actual=None, **kwargs):
        super().__init__(**kwargs)

        self._actual = actual
        self._control_target = control_target

        self._grid = GridLayout(
            cols=1,
            spacing=self.spacing,
            padding=self.padding,
            size_hint_y=None,  # height managed manually for scrolling
        )

        self._grid.bind(minimum_height=self._grid.setter("height"))
        # reflow grid on container resize
        self.bind(size=self._on_resize)

        self._empty_label = ColorLabel(
            text="No Cameras Detected",
            color=[1, 1, 1, 1],
            bgcolor=[1, 0.2, 0.2, 0.7],
            halign="center",
            valign="middle",
            font_size="32sp",
            size_hint=(1, None),
            height="52sp",
        )
        # ensure text alignment works
        self._empty_label.bind(size=lambda inst, val: setattr(inst, "text_size", val))

        self.add_widget(self._empty_label)
        # ensure initial display state is correct
        Clock.schedule_once(lambda dt: self._update_empty_state(), 0.05)

    @property
    def control_target(self):
        return self._control_target

    @property
    def actual(self):
        return self._actual

    def _propagate_setting(self, name, value):
        for widget in self.camera_widgets.values():
            setattr(widget, name, value)

    def on_show_ts(self, *_):
        self._propagate_setting('show_ts', self.show_ts)

    def on_show_key(self, *_):
        self._propagate_setting('show_key', self.show_key)

    def on_show_path(self, *_):
        self._propagate_setting('show_path', self.show_path)

    def on_show_card(self, *_):
        self._propagate_setting('show_card', self.show_card)

    def on_show_crop(self, *_):
        self._propagate_setting('show_crop', self.show_crop)

    def on_apply_crop(self, *_):
        self._propagate_setting('apply_crop', self.apply_crop)

    def on_simplify(self, *_):
        self._propagate_setting('simplify', self.simplify)

    def on_desired_width(self, *_):
        Clock.schedule_once(lambda dt: self._reflow())

    def on_run_preview(self, *_):
        self._propagate_setting('run_preview', self.run_preview)

    def on_enabled_previews(self, _, keys):
        # TODO Also apply the new state to the control target
        self._grid.clear_widgets()
        for key in keys:
            self._grid.add_widget(self.camera_widgets[key])
        self._update_empty_state()
        Clock.schedule_once(lambda dt: self._reflow())

    # ------------------------------------------------------------------
    # Camera management
    # ------------------------------------------------------------------
    def add_camera(self, camera_key, connection_path=None, camera_card=None, control_target=None):
        if camera_key in self.camera_widgets:
            return self.camera_widgets[camera_key]

        widget = CameraPreviewWidget(
            camera_key=camera_key,
            connection_path=connection_path or "N/A",
            camera_card=camera_card or "",
            control_target=control_target,
            size_hint=(None, None),
        )

        self.camera_widgets[camera_key] = widget
        return widget

    def remove_camera(self, camera_key):
        if camera_key in self.enabled_previews:
            self.enabled_previews.remove(camera_key)
        self.camera_widgets.pop(camera_key, None)

    # ------------------------------------------------------------------
    # Internal helpers: swap child of ScrollView between grid and label
    # ------------------------------------------------------------------
    def _show_grid(self):
        if self._grid in self.children:
            return
        if self._empty_label in self.children:
            self.remove_widget(self._empty_label)
        self.add_widget(self._grid)

    def _show_empty_label(self):
        if self._empty_label in self.children:
            return
        if self._grid in self.children:
            self.remove_widget(self._grid)
        self.add_widget(self._empty_label)

    def _update_empty_state(self, *args):
        if len(self.enabled_previews) == 0:
            self._show_empty_label()
        else:
            self._show_grid()

    # ------------------------------------------------------------------
    # Layout logic
    # ------------------------------------------------------------------
    def _on_resize(self, *args):
        Clock.schedule_once(lambda dt: self._reflow())

    def _reflow(self, *args):
        """Recalculate grid columns and resize children responsively."""
        n = len(self.enabled_previews)
        if n == 0:
            return

        grid_width = self.width - 2 * self.padding

        # Heuristic tuning parameters
        desired_width = self.desired_width  # target width for one preview
        min_width = desired_width * 0.7  # allow up to 30% compression

        # Start by estimating how many previews fit at desired size
        cols = max(1, int(grid_width // (desired_width + self.spacing)))

        # Ensure we have at least 1 and at most N columns
        cols = min(max(cols, 1), n)

        # Now compute actual width based on this many columns
        total_spacing = self.spacing * (cols - 1)
        available = grid_width - total_spacing
        child_width = available / cols

        # If too small, drop columns until we're above min_width
        while cols > 1 and child_width < min_width:
            cols -= 1
            total_spacing = self.spacing * (cols - 1)
            available = grid_width - total_spacing
            child_width = available / cols

        # Apply final column count
        self._grid.cols = cols

        # Maintain 4:3 aspect ratio
        child_height = child_width * 3 / 4

        # Update each preview
        for w in self.camera_widgets.values():
            w.size = (child_width, child_height)

        # Adjust grid height
        rows = (n + cols - 1) // cols
        grid_height = rows * (child_height + self.spacing) - self.spacing + 2 * self.padding
        self._grid.height = max(grid_height, self.height)
