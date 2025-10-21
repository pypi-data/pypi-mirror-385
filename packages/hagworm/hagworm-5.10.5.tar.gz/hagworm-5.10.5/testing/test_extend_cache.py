# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import pytest

from hagworm.extend.asyncio.base import Utils
from hagworm.extend.cache import StackCache


pytestmark = pytest.mark.asyncio
# pytest.skip(allow_module_level=True)


class TestCache:

    async def test_stack_cache(self):

        cache = StackCache(ttl=0.5)

        ckey = Utils.uuid1()
        cval = Utils.uuid1()

        res1 = cache.has(ckey)
        res2 = cache.size()

        assert not res1 and res2 == 0

        cache.set(ckey, cval)

        res3 = cache.has(ckey)
        res4 = cache.get(ckey)
        res5 = cache.size()

        assert res3 and res4 == cval and res5 == 1

        await Utils.sleep(1)

        res6 = cache.has(ckey)
        res7 = cache.get(ckey)
        res8 = cache.size()

        assert not res6 and res7 is None and res8 == 0
