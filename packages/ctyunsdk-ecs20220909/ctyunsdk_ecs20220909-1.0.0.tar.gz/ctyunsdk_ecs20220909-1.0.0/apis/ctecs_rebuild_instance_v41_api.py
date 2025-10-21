from typing import List, Optional, Dict, Any
from core.client import CtyunClient
from core.credential import Credential
from core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtecsRebuildInstanceV41Request:
    regionID: str  # 资源池ID，您可以查看<a href="https://www.ctyun.cn/document/10026730/10028695">地域和可用区</a>来了解资源池 <br />获取：<br /><span style="background-color: rgb(73, 204, 144);color: rgb(255,255,255);padding: 2px; margin:2px">查</span> <a  href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=5851&data=87">资源池列表查询</a>
    instanceID: str  # 云主机ID，您可以查看<a href="https://www.ctyun.cn/products/ecs">弹性云主机</a>了解云主机的相关信息<br />获取：<br /><span style="background-color: rgb(73, 204, 144);color: rgb(255,255,255);padding: 2px; margin:2px">查</span> <a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=8309&data=87">查询云主机列表</a><br /><span style="background-color: rgb(97, 175, 254);color: rgb(255,255,255);padding: 2px; margin:2px">创</span> <a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=8281&data=87">创建一台按量付费或包年包月的云主机</a><br /><span style="background-color: rgb(97, 175, 254);color: rgb(255,255,255);padding: 2px; margin:2px">创</span> <a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=8282&data=87">批量创建按量付费或包年包月云主机</a>
    userName: Optional[str] = None  # 用户名。当操作系统为非Windows使用密码登录时，用户名取值范围：<br />root（系统超级用户），<br />ecs-user（系统普通用户），<br />注：非Windows云主机用户默认为root；该参数大小写敏感
    password: Optional[str] = None  # 用户密码，密码和密钥对ID，二者必传一个。满足以下规则：<br />长度在8～30个字符;<br />必须包含大写字母、小写字母、数字以及特殊符号中的三项;<br />特殊符号可选：<br />()\`~!@#$%^&*_-+=\｜{}[]:;'<>,.?/ <br />且不能以斜线号/开头用户密码，满足以下规则：<br />长度在8～30个字符；<br />必须包含大写字母、小写字母、数字以及特殊符号中的三项；<br />特殊符号可选：()`~!@#$%^&*_-+=｜{}[]:;'<>,.?/\且不能以斜线号 / 开头；<br />不能包含3个及以上连续字符；<br />Linux镜像不能包含镜像用户名（root）、用户名的倒序（toor）、用户名大小写变化（如RoOt、rOot等），若Linux镜像用户名为ecs-user，密码不能包含用户名(ecs-user)、用户名的倒序(resu-sce)、用户名大小写变化(如ECS-USER等)；<br />Windows镜像不能包含镜像用户名（Administrator）、用户名大小写变化（adminiSTrator等）
    keyPairID: Optional[str] = None  # 密钥对ID，密码和密钥对ID，二者必传一个。请避免同时使用，同时使用时只有绑定密钥生效。<br />注：windows云主机不支持使用密钥对
    imageID: Optional[str] = None # 镜像ID，您可以查看<a href="https://www.ctyun.cn/document/10026730/10030151">镜像概述</a>来了解云主机镜像<br />获取：<br /><span style="background-color: rgb(73, 204, 144);color: rgb(255,255,255);padding: 2px; margin:2px">查</span> <a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=23&api=4763&data=89">查询可以使用的镜像资源</a><br /><span style="background-color: rgb(97, 175, 254);color: rgb(255,255,255);padding: 2px; margin:2px">创</span> <a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=23&api=4765&data=89">创建私有镜像（云主机系统盘）</a><br />注：不填默认以原镜像进行重装
    userData: Optional[str] = None  # 用户自定义数据，需要以Base64方式编码，Base64编码后的长度限制为1-16384字符
    instanceName: Optional[str] = None  # 云主机名称。不同操作系统下，云主机名称规则有差异<br />Windows：长度为2-15个字符，允许使用大小写字母、数字或连字符（-）。不能以连字符（-）开头或结尾，不能连续使用连字符（-），也不能仅使用数字；<br />其他操作系统：长度为2-64字符，允许使用点（.）分隔字符成多段，每段允许使用大小写字母、数字或连字符（-），但不能连续使用点号（.）或连字符（-），不能以点号（.）或连字符（-）开头或结尾，也不能仅使用数字<br />注：如果不填，默认值为原来云主机名称
    monitorService: Optional[bool] = None # 监控参数，支持通过该参数指定云主机在创建后是否开启详细监控，取值范围： <br />false：不开启，<br />true：开启<br />若指定该参数为true或不指定该参数，云主机内默认开启最新详细监控服务<br />若指定该参数为false，默认公共镜像不开启最新监控服务；私有镜像使用镜像中保留的监控服务<br />说明：仅部分资源池支持monitorService参数，详细请参考<a href="https://www.ctyun.cn/document/10026730/10325957">监控Agent概览</a>
    payImage: Optional[bool] = False # 付费镜像，当重装镜像为付费镜像时，该参数为True；当重装镜像为免费镜像时，该参数为False。注：默认为False
    clientToken: Optional[str] = None # 客户端存根，用于保证订单幂等性。保留时间为24小时，使用同一个clientToken值，则代表为同一个请求<br />注：当涉及付费镜像时，该参数必填；当不涉及时，该参数不支持


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if v is not None}




@dataclass
class CtecsRebuildInstanceV41ReturnObjResponse:
    jobID: Optional[str]  # 重装任务ID，您可以调用<a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=5543&data=87">查询一个异步任务的结果</a>来查询操作是否成功<br />注：当免费镜像重装时，返回该参数；当付费镜像重装时，不返回该参数
    masterOrderNO: Optional[str]  # 订单ID。注：当付费镜像重装时，返回该参数；当免费镜像重装时，不返回该参数；
    regionID: Optional[str]  # 资源池ID。注：当付费镜像重装时，返回该参数；当免费镜像重装时，不返回该参数；
    masterOrderID: Optional[str]  # 主订单ID。调用方在拿到masterOrderID之后，可以使用materOrderID进一步确认订单状态及资源状态<br />查询订单状态及资源UUID：<br /><span style="background-color: rgb(73, 204, 144);color: rgb(255,255,255);padding: 2px; margin:2px">查</span> <a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=9607&data=87&isNormal=1">根据masterOrderID查询云主机ID</a><br />注：当付费镜像重装时，返回该参数；当免费镜像重装时，不返回该参数



    @staticmethod
    def from_json(json_data: dict) -> 'CtecsRebuildInstanceV41ReturnObjResponse':
        if not json_data:
            return None
        obj = CtecsRebuildInstanceV41ReturnObjResponse(
            jobID=json_data.get('jobID'),
            masterOrderNO=json_data.get('masterOrderNO'),
            regionID=json_data.get('regionID'),
            masterOrderID=json_data.get('masterOrderID')
        )
        return obj

@dataclass
class CtecsRebuildInstanceV41Response:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str]  # 错误码，为product.module.code三段式码
    error: Optional[str]  # 错误码，为product.module.code三段式码
    message: Optional[str]  # 英文描述信息
    description: Optional[str]  # 中文描述信息
    returnObj: Optional[CtecsRebuildInstanceV41ReturnObjResponse]  # 成功时返回的数据




    @staticmethod
    def from_json(json_data: dict) -> 'CtecsRebuildInstanceV41Response':
        if not json_data:
            return None
        return_obj = None
        if 'returnObj' in json_data and json_data['returnObj']:
            return_obj = CtecsRebuildInstanceV41ReturnObjResponse.from_json(json_data['returnObj'])

        obj = CtecsRebuildInstanceV41Response(
            statusCode=json_data.get('statusCode'),
            errorCode=json_data.get('errorCode'),
            error=json_data.get('error'),
            message=json_data.get('message'),
            description=json_data.get('description'),
            returnObj=return_obj
        )
        return obj



# 该接口提供用户重装一台云主机功能，通过填写相应云主机ID、镜像ID对云主机进行重装<br/><b>准备工作：</b><br/>&emsp;&emsp;构造请求：在调用前需要了解如何构造请求，详情查看<a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=%u6784%u9020%u8BF7%u6C42&data=87&vid=81">构造请求</a><br />&emsp;&emsp;认证鉴权：openapi请求需要进行加密调用，详细查看<a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=%u8BA4%u8BC1%u9274%u6743&data=87&vid=81">认证鉴权</a><br /><b>注意事项：</b><br />&emsp;&emsp;单台操作：当前接口只能操作单台云主机，重装多台云主机请使用接口<a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=8306&data=87">重装多台云主机</a>进行操作<br/>&emsp;&emsp;异步接口：该接口为异步接口，请求过后会拿到任务ID（jobID），后续可以调用<a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=5543&data=87">查询一个异步任务的结果</a>来查询操作是否成功<br />&emsp;&emsp;监控安装：在云服务器创建成功后，3-5分钟内将完成详细监控Agent安装，即开启云服务器CPU，内存，网络，磁盘，进程等指标详细监控，若不开启，则无任何监控数据
class CtecsRebuildInstanceV41Api:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtecsRebuildInstanceV41Request) -> CtecsRebuildInstanceV41Response:
        url = endpoint + "/v4/ecs/rebuild-instance"
        try:
            request_dict = request.to_dict()
            response = client.post(url=url, data=request_dict, credential=credential)
            return CtecsRebuildInstanceV41Response.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
