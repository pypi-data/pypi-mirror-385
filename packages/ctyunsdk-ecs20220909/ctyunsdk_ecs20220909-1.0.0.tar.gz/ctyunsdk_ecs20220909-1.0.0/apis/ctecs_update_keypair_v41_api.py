from typing import List, Optional, Dict, Any
from core.client import CtyunClient
from core.credential import Credential
from core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtecsUpdateKeypairV41Request:
    regionID: str  # 资源池ID，您可以查看<a href="https://www.ctyun.cn/document/10026730/10028695">地域和可用区</a>来了解资源池 <br />获取：<br /><span style="background-color: rgb(73, 204, 144);color: rgb(255,255,255);padding: 2px; margin:2px">查</span> <a  href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=5851&data=87">资源池列表查询</a>
    keyPairID: str  # 密钥对ID，您可以查看<a href="https://www.ctyun.cn/document/10026730/10230540">密钥对</a>来了解密钥对相关内容 <br />获取：<br /><span style="background-color: rgb(73, 204, 144);color: rgb(255,255,255);padding: 2px; margin:2px">查</span> <a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=8342&data=87">查询一个或多个密钥对</a><br /><span style="background-color: rgb(97, 175, 254);color: rgb(255,255,255);padding: 2px; margin:2px">创</span> <a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=8344&data=87">创建一对SSH密钥对</a>
    keyPairDescription: Optional[str] = None # 密钥对描述。限制长度为0~255个字符。<br />注：传空字符串为去除描述信息


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if v is not None}



@dataclass
class CtecsUpdateKeypairV41ReturnObjResponse:
    """返回参数"""
    keyPairID: Optional[str]  # 被更新名称的密钥对ID
    keyPairDescription: Optional[str]  # 更新后的密钥对描述信息

    @staticmethod
    def from_json(json_data: dict) -> 'CtecsUpdateKeypairV41ReturnObjResponse':
        if not json_data:
            return None
        obj = CtecsUpdateKeypairV41ReturnObjResponse(
            keyPairID=json_data.get('keyPairID'),
            keyPairDescription=json_data.get('keyPairDescription')
        )
        return obj

@dataclass
class CtecsUpdateKeypairV41Response:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str]  # 错误码，为product.module.code三段式码
    error: Optional[str]  # 错误码，为product.module.code三段式码
    message: Optional[str]  # 失败时的错误信息，一般为英文描述
    description: Optional[str]  # 失败时的错误描述，一般为中文描述
    returnObj: Optional[CtecsUpdateKeypairV41ReturnObjResponse]  # 返回参数

    @staticmethod
    def from_json(json_data: dict) -> 'CtecsUpdateKeypairV41Response':
        if not json_data:
            return None
        return_obj = None
        if 'returnObj' in json_data and json_data['returnObj']:
            return_obj = CtecsUpdateKeypairV41ReturnObjResponse.from_json(json_data['returnObj'])

        obj = CtecsUpdateKeypairV41Response(
            statusCode=json_data.get('statusCode'),
            errorCode=json_data.get('errorCode'),
            error=json_data.get('error'),
            message=json_data.get('message'),
            description=json_data.get('description'),
            returnObj=return_obj
        )
        return obj


# 该接口提供用户更新云主机的部分信息的功能<br /><b>准备工作</b>：<br />&emsp;&emsp;构造请求：在调用前需要了解如何构造请求，详情查看<a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=%u6784%u9020%u8BF7%u6C42&data=87&vid=81">构造请求</a><br />&emsp;&emsp;认证鉴权：openapi请求需要进行加密调用，详细查看<a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=%u8BA4%u8BC1%u9274%u6743&data=87&vid=81">认证鉴权</a><br />
class CtecsUpdateKeypairV41Api:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtecsUpdateKeypairV41Request) -> CtecsUpdateKeypairV41Response:
        url = endpoint + "/v4/ecs/keypair/update-keypair"
        try:
            request_dict = request.to_dict()
            response = client.post(url=url, data=request_dict, credential=credential)
            return CtecsUpdateKeypairV41Response.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
