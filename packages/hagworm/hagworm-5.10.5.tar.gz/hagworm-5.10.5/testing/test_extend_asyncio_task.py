# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import pytest

from hagworm.extend.asyncio.base import Utils
from hagworm.extend.asyncio.task import MultiTasks, RateLimiter


pytestmark = pytest.mark.asyncio
# pytest.skip(allow_module_level=True)


class TestTasks:

    async def test_multi_tasks(self):

        async def _do_acton(val):
            await Utils.sleep(val)

        tasks = MultiTasks(5)

        tasks.append(_do_acton(8))

        for _ in range(2):

            tasks.append(_do_acton(4))

            for _ in range(2):
                tasks.append(_do_acton(1))
                tasks.append(_do_acton(1))
                tasks.append(_do_acton(2))

        await tasks

    async def test_rate_limiter(self):

        async def _temp(num):
            await Utils.sleep(num)
            return True

        limiter = RateLimiter(2, 5, 200)

        await limiter.append(_temp, 0.1)
        await limiter.append(_temp, 0.2)
        await limiter.append(_temp, 0.3)
        await limiter.append(_temp, 0.4)
        await limiter.append(_temp, 0.5)
        await limiter.append(_temp, 0.6)

        await limiter.join()
        limiter.close()
