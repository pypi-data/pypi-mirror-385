from typing import List, Optional, Dict, Any
from core.client import CtyunClient
from core.credential import Credential
from core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtecsDestroyInstanceRequest:
    clientToken: str  # 客户端存根，用于保证订单幂等性。要求单个云平台账户内唯一，使用同一个ClientToken值，其他请求参数相同时，则代表为同一个请求。保留时间为24小时
    regionID: str  # 资源池ID，您可以查看<a href="https://www.ctyun.cn/document/10026730/10028695">地域和可用区</a>来了解资源池 <br />获取：<br /><span style="background-color: rgb(73, 204, 144);color: rgb(255,255,255);padding: 2px; margin:2px">查</span> <a  href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=5851&data=87">资源池列表查询</a>
    instanceID: str  # 云主机ID，您可以查看<a href="https://www.ctyun.cn/products/ecs">弹性云主机</a>了解云主机的相关信息<br />获取：<br /><span style="background-color: rgb(73, 204, 144);color: rgb(255,255,255);padding: 2px; margin:2px">查</span> <a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=8309&data=87">查询云主机列表</a>

    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}


@dataclass
class CtecsDestroyInstanceReturnObjResponse:
    masterOrderID: Optional[str] = None  # 主订单ID。调用方在拿到masterOrderID之后，可以使用masterOrderID进一步确认订单状态及资源状态
    masterOrderNO: Optional[str] = None  # 订单号
    regionID: Optional[str] = None  # 资源池ID


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if v is not None}

    @staticmethod
    def from_json(json_data: dict) -> Optional['CtecsDestroyInstanceReturnObjResponse']:
        if not json_data:
            return None
        obj = CtecsDestroyInstanceReturnObjResponse(
            masterOrderID=json_data.get('masterOrderID'),
            masterOrderNO=json_data.get('masterOrderNO'),
            regionID=json_data.get('regionID'),
        )
        return obj


@dataclass
class CtecsDestroyInstanceResponse:
    statusCode: Any = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 英文描述信息
    description: Optional[str] = None  # 中文描述信息
    returnObj: Optional[CtecsDestroyInstanceReturnObjResponse] = None  # 成功时返回的数据


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> Optional['CtecsDestroyInstanceResponse']:
        if not json_data:
            return None

        return_obj = None
        if "returnObj" in json_data:
            returnObj = json_data.get("returnObj")
            if returnObj is not None:
                return_obj = CtecsDestroyInstanceReturnObjResponse.from_json(returnObj)

        obj = CtecsDestroyInstanceResponse(
            statusCode=json_data.get('statusCode'),
            errorCode=json_data.get('errorCode'),
            error=json_data.get('error'),
            message=json_data.get('message'),
            description=json_data.get('description'),
            returnObj=return_obj,
        )
        return obj


# 销毁一台包周期已退订云主机<br /><b>准备工作</b>：<br />&emsp;&emsp;构造请求：在调用前需要了解如何构造请求，详情查看<a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=%u6784%u9020%u8BF7%u6C42&data=87&vid=81">构造请求</a><br />&emsp;&emsp;认证鉴权：openapi请求需要进行加密调用，详细查看<a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=%u8BA4%u8BC1%u9274%u6743&data=87&vid=81">认证鉴权</a><br /><b>注意事项</b>：<br />&emsp;&emsp;1. 对于成功销毁，并重复使用clientToken再次请求的情况下，只保证返回第一次使用该clientToken时请求参数对应的主订单ID（masterOrderID）<br />&emsp;&emsp;2. 包周期已退订云主机已不再计费，但占用户资源相关配额，确认该云主机需要销毁的情况下执行该请求
class CtecsDestroyInstanceApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential, client, endpoint, request) -> CtecsDestroyInstanceResponse:
        url = endpoint + "/v4/ecs/destroy-instance"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtecsDestroyInstanceResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
