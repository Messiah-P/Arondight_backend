import asyncio

import uvicorn
from fastapi import FastAPI, Depends

from controller.common import dependencies
from controller.common.initializer import Initializer
from controller.api.plt_api import plt_api
from controller.api.pixiv_api import pixiv_api

app = FastAPI()

app.include_router(pixiv_api, prefix="/arondight/pixiv", tags=["Pixiv接口"])
app.include_router(plt_api, prefix="/arondight/plt", tags=["PLT接口"])


@app.get("/")
async def root(initializer: Initializer = Depends(dependencies.get_initializer)):
    await asyncio.sleep(100)
    return {"message": "Welcome to Use Arondight!"}


if __name__ == "__main__":
    uvicorn.run(app='main:app', host="0.0.0.0", port=8002, reload=True)
