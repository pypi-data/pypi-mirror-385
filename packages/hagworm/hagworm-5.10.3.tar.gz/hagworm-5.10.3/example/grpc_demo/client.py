# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import os
import sys
import typing
import asyncio
import grpc

os.chdir(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(r'../../'))

from hagworm.extend.asyncio.base import Utils
from hagworm.extend.asyncio.base import install_uvloop
from hagworm.third.grpc.client import GRPCClient, RobustStreamClient


class StreamClient(RobustStreamClient):

    async def on_message(self, data: typing.Any):
        Utils.log.info(str(data))

    async def on_connect(self):
        pass

    def on_close(self, stub: grpc.aio.StreamStreamCall):
        pass



async def main():

    client = GRPCClient()

    await client.open([r'127.0.0.1:8080'])

    Utils.log.info(await client.ping())

    for idx in range(10):
        try:
            Utils.log.info(
                await client.unary_unary(
                    r'/demo/unary_unary_test',
                    {r'int_field': idx, r'str_field': Utils.b64_encode(f'test_{idx}', True)}
                )
            )
        except Exception as err:
            Utils.log.error(str(err))

    ##########

    for idx in range(10):
        _messages = []
        try:
            resp = client.unary_stream(
                r'/demo/unary_stream_test',
                {r'int_field': idx, r'str_field': Utils.b64_encode(f'test_{idx}', True)}
            )
            async for _msg in resp:
                _messages.append(_msg)
            Utils.log.info(_messages)
        except Exception as err:
            Utils.log.error(str(err))

    ##########

    for idx in range(10):
        try:
            resp = client.stream_unary(r'/demo/stream_unary_test')
            for _idx in range(2):
                await resp.write({r'int_field': idx, r'str_field': f'test_{idx}_{_idx}'})
            await resp.done_writing()
            Utils.log.info(await resp)
        except Exception as err:
            Utils.log.error(str(err))

    ##########

    stream = StreamClient(client, r'/demo/stream_stream_test')
    await stream.connect()

    for idx in range(10):
        try:
            await stream.write({'stream': idx})
        except Exception as err:
            Utils.log.error(str(err))
    await stream.done_writing()

    await stream.join()


if __name__ == r'__main__':

    install_uvloop()

    asyncio.run(main())
