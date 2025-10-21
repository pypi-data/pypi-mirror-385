from ctyunsdk_ecs20220909.core.client import CtyunClient
from ctyunsdk_ecs20220909.core.credential import Credential
from ctyunsdk_ecs20220909.core.exception import CtyunRequestException

from dataclasses import dataclass
from typing import Optional, List, Any


@dataclass
class CtecsDetailsKeypairV41Request:
    regionID: str  # 资源池ID，您可以查看<a href="https://www.ctyun.cn/document/10026730/10028695">地域和可用区</a>来了解资源池 <br />获取：<br /><span style="background-color: rgb(73, 204, 144);color: rgb(255,255,255);padding: 2px; margin:2px">查</span> <a  href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=5851&data=87">资源池列表查询</a>
    projectID: Optional[str] = None # 企业项目ID，企业项目管理服务提供统一的云资源按企业项目管理，以及企业项目内的资源管理，成员管理。您可以通过查看<a href="https://www.ctyun.cn/document/10017248/10017961">创建企业项目</a>了解如何创建企业项目
    keyPairName: Optional[str] = None # 密钥对名称。满足以下规则：只能由数字、字母、-组成，不能以数字和-开头、以-结尾，且长度为2-63字符.
    queryContent: Optional[str] = None # 模糊匹配查询内容（匹配字段：keyPairName、keyPairID）
    pageNo: Any = None  # 页码，取值范围：正整数（≥1），注：默认值为1
    pageSize: Any = None # 每页记录数目，取值范围：[1, 50]，注：默认值为10


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if v is not None}



@dataclass
class CtecsDetailsKeypairV41ReturnObjResultsResponse:
    publicKey: Optional[str]  # 密钥对的公钥
    keyPairName: Optional[str]  # 密钥对名称
    fingerPrint: Optional[str]  # 密钥对的指纹，采用MD5信息摘要算法
    keyPairID: Optional[str]  # 密钥对的ID
    projectID: Optional[str]  # 企业项目ID
    keyPairDescription: Optional[str]  # 密钥对的描述

    @staticmethod
    def from_json(json_data: dict) -> 'CtecsDetailsKeypairV41ReturnObjResponse':
        if not json_data:
            return None
        results = None
        if 'results' in json_data and json_data['results']:
            results = [CtecsDetailsKeypairV41ReturnObjResultsResponse.from_json(item) if item else None for item in json_data['results']]

        obj = CtecsDetailsKeypairV41ReturnObjResponse(
            currentCount=json_data.get('currentCount'),
            totalCount=json_data.get('totalCount'),
            results=results
        )
        return obj

@dataclass
class CtecsDetailsKeypairV41ReturnObjResponse:
    currentCount: Any  # 当前页记录数目
    totalCount: Any  # 总记录数
    results: Optional[List[Optional[CtecsDetailsKeypairV41ReturnObjResultsResponse]]]  # 分页明细

    @staticmethod
    def from_json(json_data: dict) -> 'CtecsDetailsKeypairV41Response':
        if not json_data:
            return None
        return_obj = None
        if 'returnObj' in json_data and json_data['returnObj']:
            return_obj = CtecsDetailsKeypairV41ReturnObjResponse.from_json(json_data['returnObj'])

        obj = CtecsDetailsKeypairV41Response(
            statusCode=json_data.get('statusCode'),
            errorCode=json_data.get('errorCode'),
            error=json_data.get('error'),
            message=json_data.get('message'),
            description=json_data.get('description'),
            returnObj=return_obj
        )
        return obj

@dataclass
class CtecsDetailsKeypairV41Response:
    statusCode: Any  # 返回状态码(800为成功，900为处理中或失败)
    errorCode: Optional[str]  # 错误码，为product.module.code三段式码
    error: Optional[str]  # 错误码，为product.module.code三段式码
    message: Optional[str]  # 英文描述信息
    description: Optional[str]  # 中文描述信息
    returnObj: Optional[CtecsDetailsKeypairV41ReturnObjResponse]  # 成功时返回的数据


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtecsDetailsKeypairV41Response':
        if not json_data:
            return None
        obj = CtecsDetailsKeypairV41Response(None,None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 此接口提供用户查询SSH密钥对功能。系统会接收用户输入的查询条件，并返回符合条件的密钥对详细信息。用户可根据此接口的返回值了解对应条件下的密钥对信息<br /><b>准备工作</b>：<br />&emsp;&emsp;构造请求：在调用前需要了解如何构造请求，详情查看<a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=%u6784%u9020%u8BF7%u6C42&data=87&vid=81">构造请求</a><br />&emsp;&emsp;认证鉴权：openapi请求需要进行加密调用，详细查看<a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=%u8BA4%u8BC1%u9274%u6743&data=87&vid=81">认证鉴权</a><br />
class CtecsDetailsKeypairV41Api:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtecsDetailsKeypairV41Request) -> CtecsDetailsKeypairV41Response:
        url = endpoint + "/v4/ecs/keypair/details"
        try:
            request_dict = request.to_dict()
            response = client.post(url=url, data=request_dict, credential=credential)
            return CtecsDetailsKeypairV41Response.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
