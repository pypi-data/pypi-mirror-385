from kivy.properties import BooleanProperty
from twisted.internet import reactor

from kivy.metrics import dp
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy_garden.ebs.core.colors import ColorBoxLayout
from kivy_garden.ebs.core.forms import LabelledTextInput
from kivy_garden.ebs.camera.preview_control import CameraPreviewControlPanel
from kivy_garden.ebs.camera.camera_selector import CameraSelectorPanel

from ebs.linuxnode.gui.kivy.core.basenode import BaseIoTNodeGui
from ebs.linuxnode.gui.kivy.camera.mixin import CameraGuiMixin
from twisted.internet.defer import inlineCallbacks


class CameraCaptureControls(GridLayout):
    capturing = BooleanProperty(False)

    def __init__(self, target, **kwargs):
        self._target = target
        kwargs.setdefault("cols", 1)
        kwargs.setdefault("spacing", dp(10))
        kwargs.setdefault("size_hint_y", None)
        super().__init__(**kwargs)
        self.bind(minimum_height=self.setter('height'))
        self._capture_button = None
        self._outpath_input = None
        self._install_components()

    @property
    def actual(self):
        # This is a temporary interface which should be avoided if possible.
        return getattr(self._target, "actual", None)

    @inlineCallbacks
    def _capture_button_handler(self, *_):
        self.capturing = True
        if self._outpath_input.textinput.text == "<api>":
            output_dir = self.actual.camera_captures_path
            # TODO Setup publish here?
        else:
            output_dir = self._outpath_input.textinput.text

        yield self.actual.camera_capture(
            output_dir=output_dir, restart_previews=True)
        self.capturing = False

    def _install_components(self):
        if self.actual.config.camera_publish_api:
            default = "<api>"
        else:
            default = self.actual.camera_captures_path
        self._outpath_input = LabelledTextInput(
            label_text="Output Path:", default=default,
        )
        self.add_widget(self._outpath_input)

        self._capture_button = Button(
            text="Capture All", size_hint_y=None, height=dp(50)
        )
        self._capture_button.bind(on_press=self._capture_button_handler)
        self.add_widget(self._capture_button)

    def on_capturing(self, *_):
        if self.capturing:
            self._capture_button.disabled = True
            self._capture_button.text = "Capturing ..."
        else:
            self._capture_button.disabled = False
            self._capture_button.text = "Capture All"


class ExampleNode(CameraGuiMixin, BaseIoTNodeGui):
    def _gui_camera_assembly(self):
        assembly = BoxLayout(orientation='horizontal')
        assembly.add_widget(self.gui_multicam_preview)

        _controls = ColorBoxLayout(
            orientation='vertical',
            bgcolor=(0, 0, 0, 0.3),
            size_hint_x=0.6,
            size_hint_max_x=500,
        )

        _controls_scroller = ScrollView(do_scroll_x=False)
        _controls_container = StackLayout(
            orientation='bt-lr',
            spacing="8dp",
            padding="8dp"
        )

        preview_control_panel = CameraPreviewControlPanel(target=self.gui_multicam_preview)
        _controls_container.add_widget(preview_control_panel)

        _camera_selector_panel = CameraSelectorPanel(target=self.gui_multicam_preview)
        _controls_container.add_widget(_camera_selector_panel)
        self._camera_selectors = _camera_selector_panel.selectors

        capture_controls = CameraCaptureControls(target=self.gui_multicam_preview)
        _controls_container.add_widget(capture_controls)

        _controls_scroller.add_widget(_controls_container)
        _controls.add_widget(_controls_scroller)
        assembly.add_widget(_controls)
        return assembly

    def gui_setup(self):
        root = super(ExampleNode, self).gui_setup()
        self.gui_main_content.add_widget(self._gui_camera_assembly())
        return root

    def start(self):
        super().start()
        reactor.callWhenRunning(self.camera_start_previews)
        reactor.callWhenRunning(self._camera_selectors.populate)
