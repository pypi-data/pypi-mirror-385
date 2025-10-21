from typing import List, Optional, Dict, Any
from core.client import CtyunClient
from core.credential import Credential
from core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtecsDeleteKeypairV41Request:
    regionID: str  # 资源池ID，您可以查看<a href="https://www.ctyun.cn/document/10026730/10028695">地域和可用区</a>来了解资源池 <br />获取：<br /><span style="background-color: rgb(73, 204, 144);color: rgb(255,255,255);padding: 2px; margin:2px">查</span> <a  href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=5851&data=87">资源池列表查询</a>
    keyPairName: str  # 密钥对名称。满足以下规则：只能由数字、字母、-组成，不能以数字和-开头、以-结尾，且长度为2-63字符


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if v is not None}




@dataclass
class CtecsDeleteKeypairV41ReturnObjResponse:
    keyPairName: Optional[str]  # 密钥对名称




    @staticmethod
    def from_json(json_data: dict) -> 'CtecsDeleteKeypairV41ReturnObjResponse':
        if not json_data:
            return None
        obj = CtecsDeleteKeypairV41ReturnObjResponse(
            keyPairName=json_data.get('keyPairName')
        )
        return obj

@dataclass
class CtecsDeleteKeypairV41Response:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str]  # 错误码，为product.module.code三段式码
    error: Optional[str]  # 错误码，为product.module.code三段式码
    message: Optional[str]  # 英文描述信息
    description: Optional[str]  # 中文描述信息
    returnObj: Optional[CtecsDeleteKeypairV41ReturnObjResponse]  # 返回参数




    @staticmethod
    def from_json(json_data: dict) -> 'CtecsDeleteKeypairV41Response':
        if not json_data:
            return None
        return_obj = None
        if 'returnObj' in json_data and json_data['returnObj']:
            return_obj = CtecsDeleteKeypairV41ReturnObjResponse.from_json(json_data['returnObj'])

        obj = CtecsDeleteKeypairV41Response(
            statusCode=json_data.get('statusCode'),
            errorCode=json_data.get('errorCode'),
            error=json_data.get('error'),
            message=json_data.get('message'),
            description=json_data.get('description'),
            returnObj=return_obj
        )
        return obj

# 此接口供用户用来删除SSH密钥对。系统会根据您输入的SSH密钥对的名称删除对应的密钥对，并返回删除成功信息<br /><b>准备工作</b>：<br />&emsp;&emsp;构造请求：在调用前需要了解如何构造请求，详情查看<a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=%u6784%u9020%u8BF7%u6C42&data=87&vid=81">构造请求</a><br />&emsp;&emsp;认证鉴权：openapi请求需要进行加密调用，详细查看<a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=%u8BA4%u8BC1%u9274%u6743&data=87&vid=81">认证鉴权</a><br />
class CtecsDeleteKeypairV41Api:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtecsDeleteKeypairV41Request) -> CtecsDeleteKeypairV41Response:
        url = endpoint + "/v4/ecs/keypair/delete"
        try:
            request_dict = request.to_dict()
            response = client.post(url=url, data=request_dict, credential=credential)
            return CtecsDeleteKeypairV41Response.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
