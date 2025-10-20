from .config import *
from ..base.dependency import *
from ..base.processor import *
from .context import ColorResnetPreContext
from ...utility import normalizer, caster


def _pre_processing(
    input_image: np.ndarray, input_buffer: np.ndarray, input_size: int
) -> None:
    resize = cv2.resize(
        input_image, (input_size, input_size), interpolation=cv2.INTER_CUBIC
    )
    h, w, c = resize.shape
    for channel_idx in range(c):
        input_buffer[0, channel_idx, :h, :w] = resize[:, :, channel_idx]


def _post_processing(
    output_buffer: np.ndarray,  # BxCxHxW
    output_data: np.ndarray,  # BxHxWxC
) -> None:
    output_data[:] = output_buffer[:]


@register
class COLORRESNETPREProcessor(NVIDIAProcessorBase[EngineIOData, EngineIOData]):

    def __init__(
        self,
        concurrency: int,
        index: int,
        model_path: str,
        device: Literal["auto"] | int = "auto",
        normalization: str = "color-basic",
    ):
        # super
        super().__init__(
            concurrency=concurrency,
            index=index,
            model_path=model_path,
            device=device,
        )

        self.config = ColorResnetPreConfig
        self.normalizer = normalizer.NormalizerFactory.create_multi(normalization)

    async def inference(
        self, input_data: np.ndarray, output_data: np.ndarray
    ) -> np.ndarray:
        session = self.session
        _pre_processing(
            input_image=input_data,
            input_buffer=self.input_buffer,
            input_size=self.config.PATCH_SIZE,
        )
        session.run()
        _post_processing(
            output_buffer=self.output_buffer,
            output_data=output_data,
        )

    async def _run(self, input_data: EngineIOData) -> EngineIOData:
        input_vector = self.caster.cast(input_data.frame)
        self.normalizer.normalize(input_vector, 2)
        context = ColorResnetPreContext(input_vector, self.output_buffer)

        # batch inference
        await self.inference(
            input_data=context.input_vector, output_data=context.output_vector
        )

        return EngineIOData(frame_id=input_data.frame_id, frame=context.output_vector)

    def _ready_processor(self) -> bool:
        return True

    def _bind_io(self, input_data: EngineIOData):
        self.caster = caster.Caster(input_data.frame)

        # set io shape
        self.batch_size = self.config.MAX_BATCH_SIZE
        self.io_shapes = {
            "input": (
                [self.batch_size, *self.config.TRT_SHAPE_INPUT],
                np.float32,
            ),
            "output": (
                [self.batch_size, *self.config.TRT_SHAPE_OUTPUT],
                np.float32,
            ),
        }

        # init trt engine
        self.initialize_trt_session(
            required_batch_size=self.batch_size,
            io_shape=self.io_shapes,
        )

        # set io buffer
        self.input_buffer = self.session._input_bindings[0].host_buffer.reshape(
            *self.io_shapes["input"][0]
        )
        self.output_buffer = self.session._output_bindings[0].host_buffer.reshape(
            *self.io_shapes["output"][0]
        )

        return True

    def _get_live(self) -> bool:
        return True

    def _get_concurrency(self) -> int:
        return self._concurrency
