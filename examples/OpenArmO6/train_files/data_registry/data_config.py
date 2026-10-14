"""OpenArm + LinkerHand O6 absolute joint-position data configuration."""

import copy
from typing import ClassVar

from FDM.dataloader.vla.data_config.data_config_base import BaseDataConfig


class OpenArmO6DataConfig(BaseDataConfig):
    """OpenArm dual-arm + LinkerHand O6 absolute joint-position targets.

    Native ordering:
        left arm  : 0..6
        right arm : 7..13
        left O6   : 14..19
        right O6  : 20..25

    All 26 action dimensions are continuous absolute joint-position targets.
    """

    video_keys: ClassVar[list[str]] = [
        "observation.images.head",
        "observation.images.wrist_L",
        "observation.images.wrist_R",
    ]

    state_ids: ClassVar[list[int]] = list(range(26))
    action_ids: ClassVar[list[int]] = list(range(26))

    action_origin_dim = 26

    state_pad_size = 26
    action_pad_size = 26

    # O6 finger joints are continuous joint positions, not binary grippers.
    gripper_state_ids: ClassVar[list[int]] = []
    gripper_action_ids: ClassVar[list[int]] = []
    binarize_gripper = False

    # First FDM-VLM baseline is image + language only.
    disable_state = True


OPENARM_O6_3_VIEW_KEYS = [
    "observation.images.head",
    "observation.images.wrist_L",
    "observation.images.wrist_R",
]


OPENARM_O6_DATASETS = {
    "openarm_o6_pourwater": {
        "data_root": "/home/asus/datasets/OpenArm_O6_PourWater_Sim6_N17_PhaseFT_1000_FDMCompat",
        "data_weight": 1.0,
        "data_class": "lerobot_vla",
        "data_type": "openarm_o6",
        "video_keys": list(OPENARM_O6_3_VIEW_KEYS),
    }
}


ROBOT_TYPE_CONFIG_MAP = {
    "openarm_o6": OpenArmO6DataConfig(),
}


DATASET_NAMED_MIXTURES = {
    "openarm_o6_pourwater": copy.deepcopy(OPENARM_O6_DATASETS),
}
