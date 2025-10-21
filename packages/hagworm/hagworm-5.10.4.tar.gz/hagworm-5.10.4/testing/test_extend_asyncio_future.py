# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import time
import pytest

from hagworm.extend.asyncio.future import ThreadWorker


pytestmark = pytest.mark.asyncio
# pytest.skip(allow_module_level=True)


class TestWorker:

    @ThreadWorker(1)
    def _temp_for_thread_worker(self, *args, **kwargs):
        time.sleep(1)
        return True

    async def test_thread_worker(self):

        assert await self._temp_for_thread_worker()
        assert await self._temp_for_thread_worker(1, 2)
        assert await self._temp_for_thread_worker(1, 2, t1=1, t2=2)
