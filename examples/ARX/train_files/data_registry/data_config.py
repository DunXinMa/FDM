# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""ARX VR adapters retain the shared Piper-compatible recording schema."""

import os
from typing import ClassVar

from FDM.dataloader.vla.data_config.data_config_base import BaseDataConfig, BaseRelativeDataConfig


class ARXEEFDataConfig(BaseRelativeDataConfig):
    """Dual-arm ARX Cartesian state/action schema written by the VR recorder."""

    statistics_cache_key = "piper_relative"
    state_key = "state.eef"
    action_key = "action.eef"
    video_keys: ClassVar[list[str]] = [
        "observation.images.third_view",
        "observation.images.left_wrist",
        "observation.images.right_wrist",
    ]
    state_ids: ClassVar[list[int]] = list(range(14))
    action_ids: ClassVar[list[int]] = list(range(14))
    action_origin_dim = 14
    gripper_state_ids: ClassVar[list[int]] = [6, 13]
    gripper_action_ids: ClassVar[list[int]] = [6, 13]
    transformed_action_dim = 14
    use_all_columns = True
    disable_state = False
    action_space = "cartesian"


class ARXJointDataConfig(BaseDataConfig):
    """Dual-arm ARX measured joint state with absolute joint-position actions."""

    statistics_cache_key = "piper_joint"
    state_key = "state.joint"
    action_key = "action.joint"
    video_keys: ClassVar[list[str]] = ARXEEFDataConfig.video_keys
    state_ids: ClassVar[list[int]] = list(range(14))
    action_ids: ClassVar[list[int]] = list(range(14))
    action_origin_dim = 14
    gripper_state_ids: ClassVar[list[int]] = [6, 13]
    gripper_action_ids: ClassVar[list[int]] = [6, 13]
    transformed_action_dim = 14
    use_all_columns = True
    disable_state = False
    action_space = "joint_position"


ROBOT_TYPE_CONFIG_MAP = {
    "piper": ARXEEFDataConfig(),
    "piper_joint": ARXJointDataConfig(),
}


DATASET_NAMED_MIXTURES = {
    name: {
        name: {
            "data_root": os.environ.get("ARX_DATA_ROOT", "results/arx_vr"),
            "data_weight": 1.0,
            "data_class": "lerobot_vla",
            "data_type": data_type,
        },
    }
    for name, data_type in (("arx_vr", "piper"), ("arx_vr_joint", "piper_joint"))
}
