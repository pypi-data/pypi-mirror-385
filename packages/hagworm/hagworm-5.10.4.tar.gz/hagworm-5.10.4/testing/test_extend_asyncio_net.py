# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import io
import pytest

from hagworm.extend.asyncio.task import MultiTasks
from hagworm.extend.asyncio.net import HTTPClientPool, HTTPTextClientPool, HTTPJsonClientPool, Downloader


pytestmark = pytest.mark.asyncio
# pytest.skip(allow_module_level=True)

TEST_URLS = [
    r'https://lib.sinaapp.com/js/bootstrap/4.1.3/js/bootstrap.min.js.map',
    r'https://lib.sinaapp.com/js/angular.js/angular-1.2.19/angular.min.js.map',
]


class TestHTTPClient:

    async def _http_client(self, client):

        for url in TEST_URLS:
            response = await client.get(url)
            assert response

    async def _http_client_pool(self, client):

        tasks = MultiTasks()

        for url in TEST_URLS:
            tasks.append(client.get(url))

        await tasks

    async def test_http_download(self):

        downloader = Downloader()
        bytesio = io.BytesIO()

        await downloader.fetch(bytesio, r'https://www.baidu.com/img/flexible/logo/pc/result@2.png')
        await downloader.close()

        assert bytesio.__sizeof__() > 64

    async def test_http_client_pool(self):

        pool = HTTPClientPool()

        await self._http_client(pool)
        await self._http_client_pool(pool)

        await pool.close()

    async def test_http_text_client_pool(self):

        pool = HTTPTextClientPool()

        await self._http_client(pool)
        await self._http_client_pool(pool)

        await pool.close()

    async def test_http_json_client_pool(self):

        pool = HTTPJsonClientPool()

        await self._http_client(pool)
        await self._http_client_pool(pool)

        await pool.close()
