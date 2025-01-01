from pydantic import BaseModel, Field, Json
from typing import Optional


class PostReqSchema(BaseModel):
    # 请求体
    txn_code: str = Field(..., description='交易码')
    txn_subcode: str = Field(..., description='交易子码')
    entity: Optional[dict] = Field(None, description='请求内容')


class PostRespSchema(BaseModel):
    # 响应体
    resp_code: str = Field(..., description='响应码')
    resp_desc: str = Field(None, description='响应描述')
    entity: Optional[Json] = Field(None, description='响应内容')
