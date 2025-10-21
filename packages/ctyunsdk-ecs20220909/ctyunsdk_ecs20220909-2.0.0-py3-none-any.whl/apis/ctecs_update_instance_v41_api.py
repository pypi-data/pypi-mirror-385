from typing import List, Optional, Dict, Any
from core.client import CtyunClient
from core.credential import Credential
from core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtecsUpdateInstanceV41Request:
    regionID: str  # 资源池ID，您可以查看<a href="https://www.ctyun.cn/document/10026730/10028695">地域和可用区</a>来了解资源池 <br />获取：<br /><span style="background-color: rgb(73, 204, 144);color: rgb(255,255,255);padding: 2px; margin:2px">查</span> <a  href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=5851&data=87">资源池列表查询</a>
    instanceID: str  # 云主机ID，您可以查看<a href="https://www.ctyun.cn/products/ecs">弹性云主机</a>了解云主机的相关信息<br />获取：<br /><span style="background-color: rgb(73, 204, 144);color: rgb(255,255,255);padding: 2px; margin:2px">查</span> <a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=8309&data=87">查询云主机列表</a><br /><span style="background-color: rgb(97, 175, 254);color: rgb(255,255,255);padding: 2px; margin:2px">创</span> <a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=8281&data=87">创建一台按量付费或包年包月的云主机</a><br /><span style="background-color: rgb(97, 175, 254);color: rgb(255,255,255);padding: 2px; margin:2px">创</span> <a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=8282&data=87">批量创建按量付费或包年包月云主机</a>
    displayName: Optional[str] = None  # 云主机显示名称，长度为2~63个字符<br />注：displayName、instanceName、instanceDescription不可全为空
    instanceName: Optional[str] = None  # 云主机名称，支持模式串。不同操作系统下，云主机名称规则有差异<br />Windows：长度为2-15个字符，允许使用大小写字母、数字或连字符（-）。不能以连字符（-）开头或结尾，不能连续使用连字符（-），也不能仅使用数字；<br />其他操作系统：长度为2-64字符，允许使用点（.）分隔字符成多段，每段允许使用大小写字母、数字或连字符（-），但不能连续使用点号（.）或连字符（-），不能以点号（.）或连字符（-）开头或结尾，也不能仅使用数字<br />注：displayName、instanceName、instanceDescription不可全为空
    instanceDescription: Optional[str] = None  # 云主机描述信息，限制长度为0~255个字符<br />注：displayName、instanceName、instanceDescription不可全为空

    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if v is not None}


@dataclass
class CtecsUpdateInstanceV41ReturnObjResponse:
    instanceID: Optional[str] = None  # 被更新名称的云主机ID
    displayName: Optional[str] = None  # 更新后的云主机显示名称
    instanceName: Optional[str] = None  # 更新后的云主机名称
    instanceDescription: Optional[str] = None  # 更新后的云主机描述信息

    @staticmethod
    def from_json(json_data: dict) -> Optional['CtecsUpdateInstanceV41ReturnObjResponse']:
        if not json_data:
            return None
        obj = CtecsUpdateInstanceV41ReturnObjResponse(
            json_data.get('instanceID'),
            json_data.get('displayName'),
            json_data.get('instanceName'),
            json_data.get('instanceDescription'),
        )
        return obj


@dataclass
class CtecsUpdateInstanceV41Response:
    statusCode: Any = None  # 返回状态码(800为成功，900为失败)
    errorCode: Optional[str] = None  # 业务细分码，为product.module.code三段式码，详见错误码部分
    error: Optional[str] = None  # 错误码，为product.module.code三段式码，详见错误码部分
    message: Optional[str] = None  # 英文描述信息
    description: Optional[str] = None  # 中文描述信息
    returnObj: Optional[CtecsUpdateInstanceV41ReturnObjResponse] = None  # 成功时返回的数据

    @staticmethod
    def from_json(json_data: dict) -> Optional['CtecsUpdateInstanceV41Response']:
        if not json_data:
            return None

        return_obj = None
        if "returnObj" in json_data:
            returnObj = json_data.get("returnObj")
            if returnObj is not None:
                return_obj = CtecsUpdateInstanceV41ReturnObjResponse.from_json(returnObj)

        obj = CtecsUpdateInstanceV41Response(
            statusCode=json_data.get('statusCode'),
            errorCode=json_data.get('errorCode'),
            error=json_data.get('error'),
            message=json_data.get('message'),
            description=json_data.get('description'),
            returnObj=return_obj,
        )
        return obj


# 该接口提供用户更新云主机的部分信息的功能<br />目前支持更新云主机的信息为：云主机显示名称（displayName）<br /><b>准备工作</b>：<br />&emsp;&emsp;构造请求：在调用前需要了解如何构造请求，详情查看<a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=%u6784%u9020%u8BF7%u6C42&data=87&vid=81">构造请求</a><br />&emsp;&emsp;认证鉴权：openapi请求需要进行加密调用，详细查看<a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=%u8BA4%u8BC1%u9274%u6743&data=87&vid=81">认证鉴权</a><br /><b>注意事项</b>：<br />&emsp;&emsp;如果使用私有镜像创建的云主机执行该操作时，请先检查云主机内部是否安装了QGA（qemu-guest-agent）。不同操作系统请参考：<a href="https://www.ctyun.cn/document/10027726/10747194">Windows系统盘镜像文件安装QGA</a>和<a href="https://www.ctyun.cn/document/10027726/10747147">Linux系统盘镜像文件安装QGA</a><br />
class CtecsUpdateInstanceV41Api:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtecsUpdateInstanceV41Request) -> CtecsUpdateInstanceV41Response:
        url = endpoint + "/v4/ecs/update-instance"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtecsUpdateInstanceV41Response.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
