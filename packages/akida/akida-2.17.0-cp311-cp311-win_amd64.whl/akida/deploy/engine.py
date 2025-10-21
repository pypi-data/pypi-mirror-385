# ******************************************************************************
# Copyright 2020 Brainchip Holdings Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ******************************************************************************
import os
import importlib.resources
import shutil


def deploy_engine(dest_path):
    engine_path = importlib.resources.files("akida").joinpath("engine")
    dest_path = os.path.join(dest_path, "engine")
    shutil.copytree(engine_path, dest_path, dirs_exist_ok=True)
