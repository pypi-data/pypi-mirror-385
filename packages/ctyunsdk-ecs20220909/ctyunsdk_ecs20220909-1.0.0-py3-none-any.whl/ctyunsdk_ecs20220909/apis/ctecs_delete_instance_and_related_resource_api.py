from ctyunsdk_ecs20220909.core.client import CtyunClient
from ctyunsdk_ecs20220909.core.credential import Credential
from ctyunsdk_ecs20220909.core.exception import CtyunRequestException

from dataclasses import dataclass
from typing import Optional, Any


@dataclass
class CtecsDeleteInstanceAndRelatedResourceRequest:
    regionID: str  # 资源池ID，您可以查看<a href="https://www.ctyun.cn/document/10026730/10028695">地域和可用区</a>来了解资源池 <br />获取：<br /><span style="background-color: rgb(73, 204, 144);color: rgb(255,255,255);padding: 2px; margin:2px">查</span> <a  href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=5851&data=87">资源池列表查询</a>
    clientToken: str  # 客户端存根，用于保证订单幂等性。保留时间为24小时，使用同一个clientToken值，则代表为同一个请求
    instanceID: str  # 云主机ID，您可以查看<a href="https://www.ctyun.cn/products/ecs">弹性云主机</a>了解云主机的相关信息<br />获取：<br /><span style="background-color: rgb(73, 204, 144);color: rgb(255,255,255);padding: 2px; margin:2px">查</span> <a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=8309&data=87">查询云主机列表</a>
    deleteVolume: Optional[bool] = None  # 是否释放所挂载的数据盘，true（释放），false（不释放），默认值False。<br /> 注：不包含随主机一同创建的数据盘，随主机创建的盘默认随主机一同释放；所挂载的数据盘若含有硬盘快照，则不会释放
    deleteEip: Optional[bool] = None  # 是否释放所绑定的弹性公网ip，true（释放），false（不释放），默认值False。<br /> 注：不包含随主机一同创建的弹性公网ip，随主机创建的弹性公网ip默认随主机一同释放

    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}



@dataclass
class CtecsDeleteInstanceAndRelatedResourceReturnObjResponse:

    @staticmethod
    def from_json(json_data: dict) -> dict:
        return {}

@dataclass
class CtecsDeleteInstanceAndRelatedResourceResponse:
    statusCode: Any = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 英文描述信息
    description: Optional[str] = None  # 中文描述信息
    returnObj: Optional[CtecsDeleteInstanceAndRelatedResourceReturnObjResponse] = None  # 成功时返回空

    @staticmethod
    def from_json(json_data: dict) -> Optional['CtecsDeleteInstanceAndRelatedResourceResponse']:
        if not json_data:
            return None

        return_obj = None
        if "returnObj" in json_data:
            returnObj = json_data.get("returnObj")
            if returnObj is not None:
                return_obj = CtecsDeleteInstanceAndRelatedResourceReturnObjResponse.from_json(returnObj)

        obj = CtecsDeleteInstanceAndRelatedResourceResponse(
            statusCode=json_data.get('statusCode'),
            errorCode=json_data.get('errorCode'),
            error=json_data.get('error'),
            message=json_data.get('message'),
            description=json_data.get('description'),
            returnObj=return_obj,
        )
        return obj


# 支持删除云主机，并选择是否释放关联资源<br/>对于包周期的云主机为退订，最终状态会转变为包周期已退订（unsubscribed）<br/>对于按量付费的云主机为删除，删除完成后，无法再次通过云主机相关查询接口查询到该云主机信息<br/><b>准备工作</b>：<br />&emsp;&emsp;构造请求：在调用前需要了解如何构造请求，详情查看<a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=%u6784%u9020%u8BF7%u6C42&data=87&vid=81">构造请求</a><br />&emsp;&emsp;认证鉴权：openapi请求需要进行加密调用，详细查看<a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=%u8BA4%u8BC1%u9274%u6743&data=87&vid=81">认证鉴权</a><br /><b>注意事项</b>：<br />&emsp;&emsp;释放前请确保文件已进行备份，释放后不可恢复。在云主机订购时，一起订购的其他资源，比如绑定的网卡、云硬盘、弹性IP等资源，会一起被释放。非一起订购的资源，比如绑定的网卡、云硬盘、弹性IP等资源会被解绑。
class CtecsDeleteInstanceAndRelatedResourceApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtecsDeleteInstanceAndRelatedResourceRequest) -> CtecsDeleteInstanceAndRelatedResourceResponse:
        url = endpoint + "/v4/ecs/delete-instance"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtecsDeleteInstanceAndRelatedResourceResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
