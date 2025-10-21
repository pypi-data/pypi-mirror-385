from dataclasses import dataclass

from .base import Frame

#
# Control frames
#


@dataclass
class ControlFrame(Frame):
    pass


@dataclass
class StartFrame(ControlFrame):
    """This is the first frame that should be pushed down a pipeline."""

    allow_interruptions: bool = False
    enable_metrics: bool = False
    enable_usage_metrics: bool = False
    report_only_initial_ttfb: bool = False
    audio_in_sample_rate: int = 16000
    audio_out_sample_rate: int = 24000


@dataclass
class EndFrame(ControlFrame):
    """Indicates that a pipeline has ended and frame processors and pipelines
    should be shut down. If the transport receives this frame, it will stop
    sending frames to its output channel(s) and close all its threads. Note,
    that this is a control frame, which means it will received in the order it
    was sent (unline system frames).

    """

    pass


@dataclass
class SyncFrame(ControlFrame):
    """This frame is used to know when the internal pipelines have finished."""

    pass


@dataclass
class SyncNotifyFrame(ControlFrame):
    """This frame is used to know when notification has been received."""

    pass
