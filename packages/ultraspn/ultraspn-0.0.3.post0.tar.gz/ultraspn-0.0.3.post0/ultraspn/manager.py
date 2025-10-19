# MultiMolecule
# Copyright (C) 2024-Present  DanLing Team

# This file is part of MultiMolecule.

# MultiMolecule is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.

# MultiMolecule is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# For additional terms and clarifications, please refer to our License FAQ at:
# <https://multimolecule.danling.org/about/license-faq>.

import os
import threading

import gphoto2 as gp

from .controller import CameraController


class CameraManager:
    def __init__(self):
        cameras_list = gp.check_result(gp.gp_camera_autodetect())
        port_info_list = gp.PortInfoList()
        port_info_list.load()
        self.controllers = []
        for model, port_path in cameras_list:
            camera = gp.Camera()
            idx = port_info_list.lookup_path(port_path)
            camera.set_port_info(port_info_list[idx])
            camera.init()
            controller = CameraController(camera)
            self.controllers.append(controller)

    def capture_all(self, base_save_path):
        results = []
        threads = []

        def capture_worker(controller, idx):
            save_path = os.path.join(base_save_path, f"camera_{idx}")
            os.makedirs(save_path, exist_ok=True)
            result = controller.capture(save_path)
            results.append(result)

        for idx, controller in enumerate(self.controllers):
            t = threading.Thread(target=capture_worker, args=(controller, idx))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        return results
