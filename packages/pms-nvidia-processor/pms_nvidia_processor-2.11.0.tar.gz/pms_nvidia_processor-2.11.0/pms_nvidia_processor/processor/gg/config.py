from ..base.config import *


class GGConfig:
    NUMBER_OF_INPUT_CHANNELS: int = 3
    NUMBER_OF_OUTPUT_CHANNELS: int = 3
    UPSCALE_RATIO: int = 1
    PATCH_SIZE = 512
    MAX_BATCH_SIZE = 8
    MIN_BATCH_SIZE = 1
    OPT_BATCH_SIZE = MAX_BATCH_SIZE // 2
    INPUT_OVERLAB_LENGTH = 32

    PATCHER_CONFIG = PatcherIOConfig(
        patch_size=PATCH_SIZE,
        upscale_ratio=UPSCALE_RATIO,
        number_of_input_channels=NUMBER_OF_INPUT_CHANNELS,
        number_of_output_channels=NUMBER_OF_OUTPUT_CHANNELS,
        input_overlab_length=INPUT_OVERLAB_LENGTH,
    )
    TRT_CONFIG = TRTIOConfig(
        patch_size=PATCH_SIZE,
        upscale_ratio=UPSCALE_RATIO,
        number_of_input_channels=NUMBER_OF_INPUT_CHANNELS,
        number_of_output_channels=NUMBER_OF_OUTPUT_CHANNELS,
    )
