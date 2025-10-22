
from datetime import datetime

from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import LoopingCall, deferLater

from ebs.linuxnode.core.config import ElementSpec, ItemSpec
from ebs.linuxnode.gui.kivy.core.basenode import BaseIoTNodeGui

from ebs.linuxnode.camera.mixin import CameraMixin
from kivy_garden.ebs.camera import MultiCameraPreviewWidget
from kivy_garden.ebs.camera.progress import CaptureProgressOverlay


class CameraGuiMixin(CameraMixin, BaseIoTNodeGui):
    def __init__(self, *args, **kwargs):
        self._gui_multicam_preview = None
        self._gui_cameras = {}
        self._preview_loop = None
        super(CameraGuiMixin, self).__init__(*args, **kwargs)

    def install(self):
        super(CameraGuiMixin, self).install()
        _elements = {
            'camera_preview_width': ElementSpec('camera_preview', 'width', ItemSpec(int, read_only=False, fallback=320)),
            'camera_preview_show_ts': ElementSpec('camera_preview', 'show_ts', ItemSpec(bool, fallback=True)),
            'camera_preview_show_key': ElementSpec('camera_preview', 'show_key', ItemSpec(bool, fallback=True)),
            'camera_preview_show_path': ElementSpec('camera_preview', 'show_path', ItemSpec(bool, fallback=True)),
            'camera_preview_show_card': ElementSpec('camera_preview', 'show_key', ItemSpec(bool, fallback=True)),
            'camera_preview_show_crop': ElementSpec('camera_preview', 'show_crop', ItemSpec(bool, fallback=True)),
            'camera_preview_apply_crop': ElementSpec('camera_preview', 'apply_crop', ItemSpec(bool, fallback=False)),
            'camera_preview_simplify_after': ElementSpec('camera_preview', 'simplify_after', ItemSpec(int, read_only=False, fallback=10)),
            'camera_preview_fps': ElementSpec('camera_preview', 'fps', ItemSpec(int, read_only=False, fallback=10)),
            'camera_preview_aliases': ElementSpec('camera_preview', 'aliases', ItemSpec(str, read_only=True, fallback='')),
        }
        for name, spec in _elements.items():
            self.config.register_element(name, spec)

    @property
    def gui_camera_preview_aliases(self):
        # TODO Use this to enable and sequence appropriate previews
        rv = self.config.camera_preview_aliases
        rv = rv.split(',')
        rv = [x.strip() for x in rv]
        while '' in rv:
            rv.remove('')
        if len(rv) == 0:
            rv = None
        return rv

    def _gui_camera_preview_overlay_simplify(self):
        self.gui_multicam_preview.simplify = True

    @property
    def gui_multicam_preview(self):
        if not self._gui_multicam_preview:
            self._gui_multicam_preview = MultiCameraPreviewWidget(
                control_target=self.cameras, actual=self
            )
            self._gui_multicam_preview.size_hint = (1, 1)
            self._gui_multicam_preview.desired_width = self.config.camera_preview_width
            self._gui_multicam_preview.show_ts = self.config.camera_preview_show_ts
            self._gui_multicam_preview.show_key = self.config.camera_preview_show_key
            self._gui_multicam_preview.show_path = self.config.camera_preview_show_path
            self._gui_multicam_preview.show_card = self.config.camera_preview_show_card
            self._gui_multicam_preview.show_crop = self.config.camera_preview_show_crop
            self._gui_multicam_preview.apply_crop = self.config.camera_preview_apply_crop
        return self._gui_multicam_preview

    @inlineCallbacks
    def camera_start_previews(self, aliases=None):
        if aliases is None:
            aliases = self.gui_multicam_preview.enabled_previews

        yield self.cameras.preview_start(aliases=aliases)

        if self._preview_loop and self._preview_loop.running:
            self._preview_loop.stop()

        self._preview_loop = LoopingCall(self._update_preview_frames)
        self._preview_loop.start(1.0 / self.config.camera_preview_fps)

        self.gui_multicam_preview.run_preview = True

        for alias in aliases:
            cam = self.cameras.get(alias)
            if cam.errored:
                self.gui_multicam_preview.camera_widgets[alias].run_preview = False

    @inlineCallbacks
    def _update_preview_frames(self):
        for alias, entry in self._gui_cameras.items():
            if alias not in self.gui_multicam_preview.enabled_previews:
                continue

            cam = entry['cam']
            preview = entry['preview']

            if not cam.preview_running:
                continue

            if cam.errored:
                preview.errored = True
                continue

            try:
                frame = yield cam.get_preview_frame()
                if frame is None:
                    continue
                timestamp = datetime.now()
                preview.update_frame(frame, timestamp)

            except Exception as e:
                self.log.error(f"Camera [{alias}] Frame fetch error: {e}")
                preview.stop_preview()
                cam.preview_stop()
                raise e

    @inlineCallbacks
    def camera_stop_previews(self, aliases=None):
        if aliases is None:
            aliases = self.gui_multicam_preview.enabled_previews

        yield self.cameras.preview_stop(aliases=aliases)
        self.gui_multicam_preview.run_preview = False
        if getattr(self, "_preview_loop", None) and self._preview_loop.running:
            self._preview_loop.stop()

    def _progress_handler(self, progress):
        preview = self._gui_cameras[progress["key"]]["preview"]
        progressbar = self._gui_cameras[progress["key"]].get("progressbar", None)
        # This is to handle the synthetic 1/1 condition of the injected done report.
        if progress["done"] < 2 and progress["max"] > 2:
            preview.capturing = True
        else:
            preview.capturing = False
        if not progressbar:
            return
        progressbar.update_from_progress(progress)

    @inlineCallbacks
    def camera_capture(self, aliases=None, output_dir=None, restart_previews=False,
                       handler=None, handler_name=None):
        if aliases is None:
            aliases = self.gui_multicam_preview.enabled_previews

        if self.config.camera_preview_lowres:
            yield self.camera_stop_previews(aliases=aliases)

        for alias in aliases:
            progressbar = CaptureProgressOverlay()
            self._gui_cameras[alias]["preview"].add_widget(progressbar)
            self._gui_cameras[alias]["progressbar"] = progressbar

        outpaths = yield self.cameras.capture_still(
            aliases=aliases, output_dir=output_dir,
            on_progress=self._progress_handler,
            handler=handler, handler_name=handler_name
        )

        for alias in aliases:
            progressbar = self._gui_cameras[alias]["progressbar"]
            self._gui_cameras[alias]["preview"].remove_widget(progressbar)
            del self._gui_cameras[alias]["progressbar"]

        if self.config.camera_preview_lowres and restart_previews:
            yield self.camera_start_previews(aliases=aliases)

        return outpaths

    @inlineCallbacks
    def _gui_camera_init(self, alias):
        cam = yield self.cameras.get(alias)
        widget = self.gui_multicam_preview.add_camera(
            camera_key=alias,
            connection_path=cam.path,
            camera_card=cam.card,
            control_target=cam
        )
        return {'cam': cam, 'preview': widget}

    @inlineCallbacks
    def _gui_cameras_init(self):
        _ = self.gui_multicam_preview
        avail = yield self.sysinfo.cameras.available()
        for alias in avail:
            self._gui_cameras[alias] = yield self._gui_camera_init(alias)

        enabled_previews = self.gui_camera_preview_aliases or avail
        self.gui_multicam_preview.enabled_previews = enabled_previews

        if self.config.camera_preview_simplify_after:
            self.reactor.callLater(
                self.config.camera_preview_simplify_after,
                self._gui_camera_preview_overlay_simplify
            )

    def start(self):
        super(CameraGuiMixin, self).start()
        self.reactor.callWhenRunning(self._gui_cameras_init)

    def gui_setup(self):
        return super(CameraGuiMixin, self).gui_setup()
