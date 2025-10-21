#
# Copyright (c) 2024, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

import asyncio

from apipeline.notifiers.base import BaseNotifier


class EventNotifier(BaseNotifier):
    def __init__(self):
        self._event = asyncio.Event()

    async def notify(self):
        self._event.set()

    async def wait(self):
        await self._event.wait()
        self._event.clear()
