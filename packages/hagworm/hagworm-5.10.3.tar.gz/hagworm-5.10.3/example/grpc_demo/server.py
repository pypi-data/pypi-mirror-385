# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import typing

import grpc
import os
import sys

os.chdir(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(r'../../'))

from pydantic import BaseModel
from pydantic.fields import Field

from hagworm.frame.fastapi.field import Base64Type
from hagworm.third.grpc.server import Router, StreamHandler
from hagworm.third.grpc.bridge import GRPCMainProcess, GRPCWorker


router = Router(r'demo')


class FormTest(BaseModel):

    int_field: int = Field(..., description=r'int_field')
    str_field: Base64Type = Field(..., description=r'str_field')


@router.unary_unary
async def unary_unary_test(request: FormTest, _: grpc.aio.ServicerContext):
    return request.model_dump()


@router.unary_stream
async def unary_stream_test(request: FormTest, context: grpc.aio.ServicerContext):

    for i in range(2):
        await context.write(request.model_dump())


@router.stream_unary
async def stream_unary_test(request: typing.AsyncIterator, _: grpc.aio.ServicerContext):

    messages = []

    async for _message in request:
        messages.append(_message)

    return messages


class StreamStreamTest(StreamHandler):

    async def on_message(self, data: typing.Any):
        await self.write(data)

    async def on_connect(self):
        pass

    def on_close(self, context: grpc.aio.ServicerContext):
        pass

@router.stream_stream
async def stream_stream_test(request: typing.AsyncIterator, context: grpc.aio.ServicerContext):
    await StreamStreamTest(request, context).join()


if __name__ == r'__main__':

    GRPCMainProcess(
        (r'0.0.0.0', 8080), [router],
        GRPCWorker, 1,
        cpu_affinity=True
    ).run()
