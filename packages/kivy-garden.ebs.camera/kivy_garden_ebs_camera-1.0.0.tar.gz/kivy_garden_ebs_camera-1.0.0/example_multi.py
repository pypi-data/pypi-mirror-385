

import numpy as np
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy_garden.ebs.camera import MultiCameraPreviewWidget


class MultiCameraDemo(App):
    def build(self):
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        root = BoxLayout(orientation="vertical")

        # Create container for all previews
        self.multi = MultiCameraPreviewWidget()
        root.add_widget(self.multi)

        # Add a few fake cameras
        self.cameras = {}
        for i, key in enumerate(["A", "B", "C", "D"]):
            widget = self.multi.add_camera(
                camera_key=f"{key}",
                connection_path=f"pci-0:4:0.3/usb-0:1:1:{i}.0",
                camera_card=f"Some card{i}"
            )
            widget.start_preview()       # ✅ ensure visible even before first frame
            self.cameras[key] = widget

        # ✅ Start updates slightly after UI is ready
        Clock.schedule_once(lambda dt: self._start_updates(), 0.1)
        Clock.schedule_once(lambda dt: setattr(self.multi, 'preview_running', False), 5)
        Clock.schedule_once(lambda dt: setattr(self.multi, 'preview_running', True), 25)
        Clock.schedule_once(lambda dt: setattr(self.multi, 'show_card', False), 10)
        return root

    def _start_updates(self):
        """Start periodic fake frame updates."""
        Clock.schedule_interval(self._update_all_frames, 1.0 / 10.0)

    def _update_all_frames(self, dt):
        """Generate random test frames and update each camera preview."""
        for key, widget in self.cameras.items():
            frame = self._random_frame_for(key)
            timestamp = datetime.now()
            widget.update_frame(frame, timestamp)

    def _random_frame_for(self, key):
        """Make a fake noisy RGB image with slight color variation."""
        h, w = 180, 240
        base = (ord(key[-1]) * 23) % 255
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        frame[:, :, 0] = (np.random.rand(h, w) * 60 + base) % 255
        frame[:, :, 1] = (np.random.rand(h, w) * 40 + base / 2) % 255
        frame[:, :, 2] = (np.random.rand(h, w) * 30 + base / 3) % 255
        return frame


if __name__ == "__main__":
    MultiCameraDemo().run()
