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

import time

import gphoto2 as gp


class CameraController:
    def __init__(self, camera=None):
        if camera is None:
            self.camera = gp.Camera()
            self.camera.init()
        else:
            self.camera = camera

    def capture(self, save_path):
        timestamp = time.time()
        file_path = self.camera.capture(gp.GP_CAPTURE_IMAGE)
        target = f"{save_path}/{file_path.name}"
        self.camera.download_file(file_path.folder, file_path.name, target)
        return {"path": target, "timestamp": timestamp}

    def __del__(self):
        self.camera.exit()
