from ctyunsdk_ecs20220909.core.client import CtyunClient
from ctyunsdk_ecs20220909.core.credential import Credential
from ctyunsdk_ecs20220909.core.exception import CtyunRequestException

from dataclasses import dataclass
from typing import Optional, Any


@dataclass
class CtecsResetInstancePasswordV41Request:
    regionID: str  # 资源池ID，您可以查看<a href="https://www.ctyun.cn/document/10026730/10028695">地域和可用区</a>来了解资源池 <br />获取：<br /><span style="background-color: rgb(73, 204, 144);color: rgb(255,255,255);padding: 2px; margin:2px">查</span> <a  href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=5851&data=87">资源池列表查询</a>
    instanceID: str  # 云主机ID，您可以查看<a href="https://www.ctyun.cn/products/ecs">弹性云主机</a>了解云主机的相关信息<br />获取：<br /><span style="background-color: rgb(73, 204, 144);color: rgb(255,255,255);padding: 2px; margin:2px">查</span> <a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=8309&data=87">查询云主机列表</a><br /><span style="background-color: rgb(97, 175, 254);color: rgb(255,255,255);padding: 2px; margin:2px">创</span> <a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=8281&data=87">创建一台按量付费或包年包月的云主机</a><br /><span style="background-color: rgb(97, 175, 254);color: rgb(255,255,255);padding: 2px; margin:2px">创</span> <a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=8282&data=87">批量创建按量付费或包年包月云主机</a>
    newPassword: str  # 新的用户密码，满足以下规则：<br />长度在8～30个字符；<br />必须包含大写字母、小写字母、数字以及特殊符号中的三项；<br />特殊符号可选：()`~!@#$%^&*_-+=｜{}[]:;'<>,.?/且不能以斜线号 / 开头；<br />不能包含3个及以上连续字符；<br />Linux镜像不能包含镜像用户名（root）、用户名的倒序（toor）、用户名大小写变化（如RoOt、rOot等），若Linux镜像用户名为ecs-user，密码不能包含用户名(ecs-user)、用户名的倒序(resu-sce)、用户名大小写变化(如ECS-USER等)；<br />Windows镜像不能包含镜像用户名（Administrator）、用户名大小写变化（adminiSTrator等），若Windows镜像已修改用户名请确保密码不包含新用户名或其大小写变体
    userName: Optional[str] = None # 用户名，当非Windows云主机存在ecs-user用户，重置密码可选用户可选：<br />root（系统超级用户），<br />ecs-user（系统普通用户）；当Windows云主机重置密码时用户名默认为administrator，若用户对administrator用户名进行了修改，应设置为修改后的用户名<br />注：非Windows云主机用户默认为root，大小写敏；Windows云主机用户默认为administrator，大小写不敏感


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if v is not None}



@dataclass
class CtecsResetInstancePasswordV41ReturnObjResponse:
    instanceID: Optional[str]  # 被更新密码的云主机ID




    @staticmethod
    def from_json(json_data: dict) -> 'CtecsResetInstancePasswordV41ReturnObjResponse':
        if not json_data:
            return None
        obj = CtecsResetInstancePasswordV41ReturnObjResponse(
            instanceID=json_data.get('instanceID')
        )
        return obj

@dataclass
class CtecsResetInstancePasswordV41Response:
    statusCode: Any  # 返回状态码(800为成功，900为失败)
    errorCode: Optional[str]  # 业务细分码，为product.module.code三段式码，详见错误码部分  
    error: Optional[str]  # 错误码，为product.module.code三段式码，详见错误码部分   
    message: Optional[str]  # 英文描述信息
    description: Optional[str]  # 中文描述信息
    returnObj: Optional[CtecsResetInstancePasswordV41ReturnObjResponse]  # 成功时返回的数据





    @staticmethod
    def from_json(json_data: dict) -> 'CtecsResetInstancePasswordV41Response':
        if not json_data:
            return None
        return_obj = None
        if 'returnObj' in json_data and json_data['returnObj']:
            return_obj = CtecsResetInstancePasswordV41ReturnObjResponse.from_json(json_data['returnObj'])

        obj = CtecsResetInstancePasswordV41Response(
            statusCode=json_data.get('statusCode'),
            errorCode=json_data.get('errorCode'),
            error=json_data.get('error'),
            message=json_data.get('message'),
            description=json_data.get('description'),
            returnObj=return_obj
        )
        return obj



# 该接口提供用户更新云主机的密码的功能<br /><b>准备工作</b>：<br />&emsp;&emsp;构造请求：在调用前需要了解如何构造请求，详情查看<a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=%u6784%u9020%u8BF7%u6C42&data=87&vid=81">构造请求</a><br />&emsp;&emsp;认证鉴权：openapi请求需要进行加密调用，详细查看<a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=%u8BA4%u8BC1%u9274%u6743&data=87&vid=81">认证鉴权</a><br /><b>注意事项</b>：<br />&emsp;&emsp;如果使用私有镜像创建的云主机执行该操作时，请先检查云主机内部是否安装了QGA（qemu-guest-agent）。不同操作系统请参考：<a href="https://www.ctyun.cn/document/10027726/10747194">Windows系统盘镜像文件安装QGA</a>和<a href="https://www.ctyun.cn/document/10027726/10747147">Linux系统盘镜像文件安装QGA</a><br />
class CtecsResetInstancePasswordV41Api:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtecsResetInstancePasswordV41Request) -> CtecsResetInstancePasswordV41Response:
        url = endpoint + "/v4/ecs/reset-password"
        try:
            request_dict = request.to_dict()
            response = client.post(url=url,  data=request_dict, credential=credential)
            return CtecsResetInstancePasswordV41Response.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
