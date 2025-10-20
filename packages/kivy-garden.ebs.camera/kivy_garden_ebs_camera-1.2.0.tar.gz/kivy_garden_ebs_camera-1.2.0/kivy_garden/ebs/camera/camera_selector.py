

from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.properties import DictProperty
from kivy.properties import ObjectProperty

from kivy.uix.button import Button
from kivy.uix.switch import Switch
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup

from kivy_garden.ebs.core.labels import SelfScalingOneLineLabel
from kivy_garden.ebs.core.panels import ExpansionPanel
from kivy_garden.ebs.core.colors import ColorBoxLayout


class CameraSelector(ColorBoxLayout):
    alias = StringProperty()
    cam_info = DictProperty()
    parent_selectors = ObjectProperty()

    def __init__(self, alias, cam_info, parent_selectors, **kwargs):
        super().__init__(orientation='horizontal',
                         size_hint_y=None,
                         height=dp(72),
                         padding=(dp(8), dp(4)),
                         spacing=dp(4),
                         bgcolor=[0.1, 0.2, 0.1, 0.7],
                         bgradius=[dp(6)],
                         **kwargs)

        self.alias = alias
        self.cam_info = cam_info
        self.parent_selectors = parent_selectors
        self._build_widget()

    def _build_widget(self):
        alias_box = BoxLayout(orientation='vertical', size_hint_x=None, width=dp(80))
        alias_lbl = SelfScalingOneLineLabel(
            text=f"{self.alias}",
            halign='center',
            valign='middle',
            size_hint_y=1,
            bold=True,
        )
        alias_box.add_widget(alias_lbl)
        self.add_widget(alias_box)

        info_box = BoxLayout(orientation='vertical', spacing=dp(2))

        res_lbl = SelfScalingOneLineLabel(
            text=self.cam_info["resolution"],
            halign='left',
            valign='middle',
            size_hint_y=None,
            height=dp(20),
        )
        path_lbl = SelfScalingOneLineLabel(
            text=self.cam_info["path"],
            halign='left',
            valign='middle',
            size_hint_y=None,
            height=dp(18),
        )
        card_lbl = SelfScalingOneLineLabel(
            text=self.cam_info.get('card'),
            halign='left',
            valign='middle',
            size_hint_y=None,
            height=dp(18),
        )
        info_box.add_widget(res_lbl)
        info_box.add_widget(path_lbl)
        info_box.add_widget(card_lbl)
        self.add_widget(info_box)

        controls_box = BoxLayout(
            orientation='vertical',
            spacing=dp(4),
            size_hint_x=0.3,
        )

        sw = Switch(size_hint=(None, 1), width=(dp(60)))
        sw.active = self.alias in getattr(self.parent_selectors.target, "enabled_previews", [])
        sw.bind(active=self._on_toggle)
        controls_box.add_widget(sw)

        # settings_btn = Button(
        #     text="⚙",
        #     size_hint=(None, None),
        #     size=(dp(40), dp(30)),
        #     on_release=self._show_settings,
        # )
        # controls_box.add_widget(settings_btn)

        self.add_widget(controls_box)
        self._controls_box = controls_box
        self._switch = sw

    # --- internal helpers ---
    def _on_toggle(self, _, value):
        enabled = self.parent_selectors.target.enabled_previews
        if value:
            self.bgcolor = [0.1, 0.2, 0.1, 0.7]
        else:
            self.bgcolor = [0.2, 0.1, 0.1, 0.7]
        if value and self.alias not in enabled:
            self.parent_selectors.target.enabled_previews.append(self.alias)
        elif not value and self.alias in enabled:
            self.parent_selectors.target.enabled_previews.remove(self.alias)

    def _show_settings(self, *_):
        """Show popup with camera details."""
        info = self.cam_info
        text = (
            f"[b]Alias:[/b] {self.alias}\n"
            f"[b]Card:[/b] {info.get('card')}\n"
            f"[b]Path:[/b] {info.get('path')}\n"
            f"[b]Resolution:[/b] {info.get('resolution')}\n"
        )
        popup = Popup(
            title=f"Camera Settings - {self.alias}",
            size_hint=(0.8, 0.4),
            content=SelfScalingOneLineLabel(text=text, markup=True, halign='left', valign='middle'),
        )
        popup.open()


class CameraSelectors(BoxLayout):
    def __init__(self, target, **kwargs):
        self._target = target
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = "8dp"
        self.padding = ("16dp", "8dp", "16dp", "8dp")
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))

    def populate(self):
        self.clear_widgets()

        sorted_items = sorted(
            self.target.camera_widgets.items(),
            key=lambda item: (len(item[0]), item[0])
        )

        for alias, preview in sorted_items:
            cam = preview.control_target
            fss = cam.frame_spec_still
            info = {
                "card": cam.card,
                "path": cam.path,
                "resolution": f"{fss.get('width', '?')}×{fss.get('height', '?')}",
            }
            sel = CameraSelector(alias=alias, cam_info=info, parent_selectors=self)
            self.add_widget(sel)

    @property
    def target(self):
        return self._target

class CameraSelectorPanel(ExpansionPanel):
    def __init__(self, target, **kwargs):
        self._target = target
        kwargs.setdefault("title", "Cameras")
        super().__init__(**kwargs)
        self.selectors = CameraSelectors(target=self._target)
        self.add_body_widget(self.selectors)
