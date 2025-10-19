

from kivy.metrics import dp
from kivy.uix.label import Label
from kivy.uix.switch import Switch
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy_garden.ebs.core.panels import ExpansionPanel


class LabelledPropSwitch(BoxLayout):
    def __init__(self, label, target_obj, prop_name: str, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height='40dp', **kwargs)

        lbl = Label(text=label, halign='left', valign='middle', size_hint_x=1)
        lbl.bind(size=lbl.setter('text_size'))
        self.add_widget(lbl)

        sw = Switch(size_hint_x=None)
        sw.active = getattr(target_obj, prop_name)
        sw.bind(active=lambda _, v: setattr(target_obj, prop_name, v))
        target_obj.bind(**{prop_name: lambda _, v: setattr(sw, 'active', v)})
        self.add_widget(sw)


class CameraPreviewOptions(BoxLayout):
    def __init__(self, target, **kwargs):
        self._target = target
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = "8dp"
        self.padding = ("16dp", "8dp", "16dp", "8dp")
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))
        self._install_switches()

    _switches = [
        ("Show Timestamp", "show_ts"),
        ("Show Camera Key", "show_key"),
        ("Show Camera Path", "show_path"),
        ("Show Camera Card", "show_card"),
        ("Show Crop Boundary", "show_crop"),
        ("Apply Crop", "apply_crop"),
    ]

    def _install_switches(self):
        for label, prop in self._switches:
            self.add_widget(
                LabelledPropSwitch(label, self._target, prop)
            )


class CameraPreviewControls(GridLayout):
    def __init__(self, target, **kwargs):
        self._target = target
        kwargs.setdefault("cols", 3)
        kwargs.setdefault("spacing", dp(10))
        kwargs.setdefault("size_hint_y", None)
        super().__init__(**kwargs)
        self.bind(minimum_height=self.setter('height'))
        self._pause_button = None
        self._save_button = None
        self._install_buttons()

    @property
    def control_target(self):
        # control_target needs to exist as a property of the target widget,
        # and should provide predefined interfaces for various control actions
        return getattr(self._target, "control_target", None)

    @property
    def actual(self):
        # This is a temporary interface which should be avoided if possible.
        return getattr(self._target, "actual", None)

    def _pause_button_handler(self, *_):
        if self._pause_button.text == "Pause Preview":
            self._pause_button.text = "Run Preview"
            self.actual.camera_stop_previews()
        else:
            self._pause_button.text = "Pause Preview"
            self.actual.camera_start_previews()

    def _save_button_handler(self, *_):
        pass

    def _install_buttons(self):
        self._pause_button = Button(text="Pause Preview", size_hint_y=None, height=dp(40))
        self._pause_button.bind(on_press=self._pause_button_handler)
        self.add_widget(self._pause_button)
        if not self.actual:
            self._pause_button.enabled = False

        self._save_button = Button(text="Save Defaults", size_hint_y=None, height=dp(40))
        self._save_button.bind(on_press=self._save_button_handler)
        self.add_widget(self._save_button)


class CameraPreviewControlPanel(ExpansionPanel):
    def __init__(self, target, **kwargs):
        self._target = target
        kwargs.setdefault("title", "Preview Controls")
        super().__init__(**kwargs)
        self._options = CameraPreviewOptions(target=self._target)
        self.add_body_widget(self._options)
        self._controls = CameraPreviewControls(target=self._target)
        self.add_body_widget(self._controls)
