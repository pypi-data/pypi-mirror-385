from typing import List, Optional, Dict, Any
from core.client import CtyunClient
from core.credential import Credential
from core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtecsCreateKeypairV41Request:
    regionID: str  # 资源池ID，您可以查看<a href="https://www.ctyun.cn/document/10026730/10028695">地域和可用区</a>来了解资源池 <br />获取：<br /><span style="background-color: rgb(73, 204, 144);color: rgb(255,255,255);padding: 2px; margin:2px">查</span> <a  href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=5851&data=87">资源池列表查询</a>
    keyPairName: str  # 密钥对名称。满足以下规则：只能由数字、字母、-组成，不能以数字和-开头、以-结尾，且长度为2-63字符
    projectID: Optional[str] = None # 企业项目ID，企业项目管理服务提供统一的云资源按企业项目管理，以及企业项目内的资源管理，成员管理。您可以通过查看<a href="https://www.ctyun.cn/document/10017248/10017961">创建企业项目</a>了解如何创建企业项目<br />注：默认值为"0"
    keyPairDescription: Optional[str] = None  # 密钥对描述。满足以下规则：长度为0~255个字符。<br />注：只多可用区资源池支持描述


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if v is not None}

@dataclass
class CtecsCreateKeypairV41ReturnObjResponse:
    keyPairName: Optional[str]  # 密钥对名称
    fingerPrint: Optional[str]  # 密钥对的指纹，采用MD5信息摘要算法
    keyPairID: Optional[str]  # 密钥对的ID
    publicKey: Optional[str]  # 密钥对的公钥
    privateKey: Optional[str]  # 密钥对的私钥
    keyPairDescription: Optional[str]  # 密钥对的描述


    @staticmethod
    def from_json(json_data: dict) -> 'CtecsCreateKeypairV41ReturnObjResponse':
        if not json_data:
            return None
        obj = CtecsCreateKeypairV41ReturnObjResponse(
            keyPairName=json_data.get('keyPairName'),
            fingerPrint=json_data.get('fingerPrint'),
            keyPairID=json_data.get('keyPairID'),
            publicKey=json_data.get('publicKey'),
            privateKey=json_data.get('privateKey'),
            keyPairDescription=json_data.get('keyPairDescription')
        )
        return obj

@dataclass
class CtecsCreateKeypairV41Response:
    statusCode: Any  # 返回状态码（800为成功，900为处理中或失败）
    errorCode: Optional[str]  # 错误码，为product.module.code三段式码
    error: Optional[str]  # 错误码，为product.module.code三段式码
    message: Optional[str]  # 英文描述信息
    description: Optional[str]  # 中文描述信息
    returnObj: Optional[CtecsCreateKeypairV41ReturnObjResponse]  # 返回参数


    @staticmethod
    def from_json(json_data: dict) -> 'CtecsCreateKeypairV41Response':
        if not json_data:
            return None
        return_obj = None
        if 'returnObj' in json_data and json_data['returnObj']:
            return_obj = CtecsCreateKeypairV41ReturnObjResponse.from_json(json_data['returnObj'])

        obj = CtecsCreateKeypairV41Response(
            statusCode=json_data.get('statusCode'),
            errorCode=json_data.get('errorCode'),
            error=json_data.get('error'),
            message=json_data.get('message'),
            description=json_data.get('description'),
            returnObj=return_obj
        )
        return obj



# 此接口用来创建一对SSH密钥对。系统会为您保管密钥的公钥部分，并返回未加密私钥。您需要自行妥善保管私钥部分<br /><b>准备工作</b>：<br />&emsp;&emsp;构造请求：在调用前需要了解如何构造请求，详情查看<a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=%u6784%u9020%u8BF7%u6C42&data=87&vid=81">构造请求</a><br />&emsp;&emsp;认证鉴权：openapi请求需要进行加密调用，详细查看<a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=%u8BA4%u8BC1%u9274%u6743&data=87&vid=81">认证鉴权</a><br />
class CtecsCreateKeypairV41Api:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtecsCreateKeypairV41Request) -> CtecsCreateKeypairV41Response:
        url = endpoint + "/v4/ecs/keypair/create-keypair"
        try:
            request_dict = request.to_dict()
            response = client.post(url=url, data=request_dict, credential=credential)
            return CtecsCreateKeypairV41Response.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
