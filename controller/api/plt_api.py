from fastapi import APIRouter, Depends
from controller.common.initializer import Initializer
from controller.common import dependencies
from controller.adapter.plt.plt_input_adapter import PltInputAdapter
from controller.service.plt.executor.plt_executor import PltExecutor
from controller.common.schema import PostRespSchema, PostReqSchema

plt_api = APIRouter()


@plt_api.post("/", response_model=PostRespSchema)
async def pixiv(request: PostReqSchema, initializer: Initializer = Depends(dependencies.get_initializer)):
    adapter = PltInputAdapter()
    executor = PltExecutor(module_base="controller.service.plt.transaction")
    txn_code, txn_subcode = adapter.decoder(request)
    resp_code, resp_desc, entity = await executor.execute(initializer, txn_code, txn_subcode, request.entity)
    resp = PostRespSchema(resp_code=resp_code, resp_desc=resp_desc)
    resp.entity = entity
    return resp
