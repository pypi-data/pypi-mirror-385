from mujoco import viewer
import numpy as np
import mujoco


class MjviewerRenderer:
    def __init__(
        self,
        model,
        data,
        cam_config,
        camera_id=None,
        camera_name=None,
        hide_menu=True,
    ):
        self.model = model
        self.data = data
        self.viewer = None
        self.camera_config = cam_config
        self.hide_menu = hide_menu
        if camera_id is not None and camera_name is not None:
            raise ValueError(
                "Both `camera_id` and `camera_name` cannot be"
                " specified at the same time."
            )
        no_camera_specified = camera_name is None and camera_id is None
        if no_camera_specified:
            camera_name = "track"

        if camera_id is None:
            self.camera_id = mujoco.mj_name2id(
                self.model,
                mujoco.mjtObj.mjOBJ_CAMERA,
                camera_name,
            )
        else:
            self.camera_id = camera_id

    def render(self, render_mode: str):
        assert render_mode == "human", (
            "MjviewerRenderer only supports human render mode"
        )
        viewer = self._get_viewer(render_mode)
        viewer.sync()

    def _get_viewer(self, render_mode: str):
        assert render_mode == "human", (
            "MjviewerRenderer only supports human render mode"
        )
        if self.viewer is None:
            self.viewer = viewer.launch_passive(
                self.model,
                self.data,
                show_left_ui=not self.hide_menu,
                show_right_ui=not self.hide_menu,
            )
            self._set_cam_config()
            if self.camera_id is not None:
                if self.camera_id >= 0:
                    self.viewer.cam.type = 2
                    self.viewer.cam.fixedcamid = self.camera_id
                else:
                    self.viewer.cam.type = 0
        return self.viewer

    def close(self):
        self.model = None
        self.data = None
        if self.viewer is not None:
            self.viewer.close()
            self.viewer = None

    def _set_cam_config(self):
        """Set the default camera parameters"""
        assert self.viewer is not None
        if self.camera_config is not None:
            for key, value in self.camera_config.items():
                if isinstance(value, np.ndarray):
                    getattr(self.viewer.cam, key)[:] = value
                else:
                    setattr(self.viewer.cam, key, value)
