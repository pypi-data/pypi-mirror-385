from typing import List

from apipeline.frames.control_frames import EndFrame
from apipeline.pipeline.pipeline import Pipeline


class SequentialMergePipeline(Pipeline):
    """This class merges the sink queues from a list of pipelines. Frames from
    each pipeline's sink are merged in the order of pipelines in the list."""

    def __init__(self, pipelines: List[Pipeline]):
        super().__init__([])
        self.pipelines = pipelines

    async def run_pipeline(self):
        for idx, pipeline in enumerate(self.pipelines):
            while True:
                frame = await pipeline.sink.get()
                if isinstance(frame, EndFrame):
                    break
                await self.sink.put(frame)

        await self.sink.put(EndFrame())
