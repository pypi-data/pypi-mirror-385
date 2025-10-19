import numpy as np
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window

from kivy_garden.ebs.camera import CameraPreviewWidget  # assuming same directory


class SingleCameraDemo(App):
    def build(self):
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        layout = BoxLayout(orientation="vertical", padding=0)

        self.preview = CameraPreviewWidget(
            camera_key="A",
            connection_path="pci-0:4:0.3/usb-0:1:1:1.0",
            camera_card="RNG"
        )

        layout.add_widget(self.preview)

        self.preview.start_preview()
        Clock.schedule_interval(self.generate_random_frame, 1.0 / 10.0)  # 10 FPS
        Clock.schedule_once(self.preview.stop_preview, 10)
        Clock.schedule_once(self.preview.start_preview, 20)
        return layout

    def generate_random_frame(self, dt):
        """Simulate a random RGB image."""
        h, w = 240, 320
        frame = (np.random.rand(h, w, 3) * 255).astype(np.uint8)
        self.preview.update_frame(frame)


if __name__ == "__main__":
    SingleCameraDemo().run()
