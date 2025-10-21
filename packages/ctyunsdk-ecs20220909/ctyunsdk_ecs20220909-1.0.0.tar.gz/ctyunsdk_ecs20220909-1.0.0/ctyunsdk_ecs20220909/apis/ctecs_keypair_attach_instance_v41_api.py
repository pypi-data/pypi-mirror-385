from ctyunsdk_ecs20220909.core.client import CtyunClient
from ctyunsdk_ecs20220909.core.credential import Credential
from ctyunsdk_ecs20220909.core.exception import CtyunRequestException

from dataclasses import dataclass
from typing import Optional, Any


@dataclass
class CtecsKeypairAttachInstanceV41Request:
    regionID: str  # 资源池ID，您可以查看<a href="https://www.ctyun.cn/document/10026730/10028695">地域和可用区</a>来了解资源池 <br />获取：<br /><span style="background-color: rgb(73, 204, 144);color: rgb(255,255,255);padding: 2px; margin:2px">查</span> <a  href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=5851&data=87">资源池列表查询</a>
    keyPairName: str  # 密钥对名称。满足以下规则：只能由数字、字母、-组成，不能以数字和-开头、以-结尾，且长度为2-63字符
    instanceID: str  # 云主机ID，您可以查看<a href="https://www.ctyun.cn/products/ecs">弹性云主机</a>了解云主机的相关信息<br />获取：<br /><span style="background-color: rgb(73, 204, 144);color: rgb(255,255,255);padding: 2px; margin:2px">查</span> <a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=8309&data=87">查询云主机列表</a><br /><span style="background-color: rgb(97, 175, 254);color: rgb(255,255,255);padding: 2px; margin:2px">创</span> <a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=8281&data=87">创建一台按量付费或包年包月的云主机</a><br /><span style="background-color: rgb(97, 175, 254);color: rgb(255,255,255);padding: 2px; margin:2px">创</span> <a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=8282&data=87">批量创建按量付费或包年包月云主机</a>

    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if v is not None}


@dataclass
class CtecsKeypairAttachInstanceV41ReturnObjResponse:
    instanceID: Optional[str]  # 云主机ID

    @staticmethod
    def from_json(json_data: dict) -> 'CtecsKeypairAttachInstanceV41ReturnObjResponse':
        if not json_data:
            return None
        obj = CtecsKeypairAttachInstanceV41ReturnObjResponse(
            instanceID=json_data.get('instanceID')
        )
        return obj

@dataclass
class CtecsKeypairAttachInstanceV41Response:
    statusCode: Any  # 返回状态码(800为成功，900为处理中或失败)
    errorCode: Optional[str]  # 错误码，为product.module.code三段式码
    error: Optional[str]  # 错误码，为product.module.code三段式码
    message: Optional[str]  # 英文描述信息
    description: Optional[str]  # 中文描述信息
    returnObj: Optional[CtecsKeypairAttachInstanceV41ReturnObjResponse]  # 返回参数

    @staticmethod
    def from_json(json_data: dict) -> 'CtecsKeypairAttachInstanceV41Response':
        if not json_data:
            return None
        return_obj = None
        if 'returnObj' in json_data and json_data['returnObj']:
            return_obj = CtecsKeypairAttachInstanceV41ReturnObjResponse.from_json(json_data['returnObj'])

        obj = CtecsKeypairAttachInstanceV41Response(
            statusCode=json_data.get('statusCode'),
            errorCode=json_data.get('errorCode'),
            error=json_data.get('error'),
            message=json_data.get('message'),
            description=json_data.get('description'),
            returnObj=return_obj
        )
        return obj


# 此接口提供用户绑定SSH密钥对到云主机功能。系统会接收用户输入的云主机id和SSH密钥对，将对应SSH密钥对绑定到对应云主机上<br /><b>准备工作</b>：<br />&emsp;&emsp;构造请求：在调用前需要了解如何构造请求，详情查看<a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=%u6784%u9020%u8BF7%u6C42&data=87&vid=81">构造请求</a><br />&emsp;&emsp;认证鉴权：openapi请求需要进行加密调用，详细查看<a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=%u8BA4%u8BC1%u9274%u6743&data=87&vid=81">认证鉴权</a><br /><b>注意事项</b>：<br />&emsp;&emsp;如果实例已经绑定了SSH密钥对，新的SSH密钥对自动替换原来的SSH密钥对 <br />
class CtecsKeypairAttachInstanceV41Api:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtecsKeypairAttachInstanceV41Request) -> CtecsKeypairAttachInstanceV41Response:
        url = endpoint + "/v4/ecs/keypair/attach-instance"
        try:
            request_dict = request.to_dict()
            response = client.post(url=url, data=request_dict, credential=credential)
            return CtecsKeypairAttachInstanceV41Response.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
