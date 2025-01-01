import asyncio

from fastapi import APIRouter, Depends

from controller.common.schema import PostReqSchema, PostRespSchema
from controller.adapter.pixiv.pixiv_input_adapter import PixivInputAdapter
from controller.service.pixiv.executor.pixiv_executor import PixivExecutor
from controller.common.initializer import Initializer
from controller.common import dependencies

pixiv_api = APIRouter()


@pixiv_api.post("/", response_model=PostRespSchema)
async def pixiv(request: PostReqSchema, initializer: Initializer = Depends(dependencies.get_initializer)):
    adapter = PixivInputAdapter()
    executor = PixivExecutor(module_base="controller.service.pixiv.transaction")
    txn_code, txn_subcode = adapter.decoder(request)
    resp_code, resp_desc, entity = await executor.execute(initializer, txn_code, txn_subcode, request.entity)
    resp = PostRespSchema(resp_code=resp_code, resp_desc=resp_desc)
    resp.entity = entity
    return resp
