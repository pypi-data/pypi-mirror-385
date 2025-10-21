from ctyunsdk_ecs20220909.core.client import CtyunClient
from ctyunsdk_ecs20220909.core.credential import Credential
from ctyunsdk_ecs20220909.core.exception import CtyunRequestException

from dataclasses import dataclass
from typing import Optional, Any


@dataclass
class CtecsUpdateFlavorSpecV41Request:
    regionID: str  # 资源池ID，您可以查看<a href="https://www.ctyun.cn/document/10026730/10028695">地域和可用区</a>来了解资源池 <br />获取：<br /><span style="background-color: rgb(73, 204, 144);color: rgb(255,255,255);padding: 2px; margin:2px">查</span> <a  href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=5851&data=87">资源池列表查询</a>
    instanceID: str  # 云主机ID，您可以查看<a href="https://www.ctyun.cn/products/ecs">弹性云主机</a>了解云主机的相关信息<br />获取：<br /><span style="background-color: rgb(73, 204, 144);color: rgb(255,255,255);padding: 2px; margin:2px">查</span> <a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=8309&data=87">查询云主机列表</a><br /><span style="background-color: rgb(97, 175, 254);color: rgb(255,255,255);padding: 2px; margin:2px">创</span> <a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=8281&data=87">创建一台按量付费或包年包月的云主机</a><br /><span style="background-color: rgb(97, 175, 254);color: rgb(255,255,255);padding: 2px; margin:2px">创</span> <a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=8282&data=87">批量创建按量付费或包年包月云主机</a>
    flavorID: str  # 云主机规格ID，您可以查看<a href="https://www.ctyun.cn/document/10026730/10118193">规格说明</a>了解弹性云主机的选型基本信息<br />获取：<br /><span style="background-color: rgb(73, 204, 144);color: rgb(255,255,255);padding: 2px; margin:2px">查</span> <a  href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=8327&data=87">查询一个或多个云主机规格资源</a>
    clientToken: str  # 客户端存根，用于保证订单幂等性。要求单个云平台账户内唯一，使用同一个clientToken值，则代表为同一个请求。保留时间为24小时
    payVoucherPrice: Any = None  # 代金券，满足以下规则：<br />两位小数，不足两位自动补0，超过两位小数无效<br />不可为负数<br />注：字段为0时表示不使用代金券，默认不使用代金券


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if v is not None}




@dataclass
class CtecsUpdateFlavorSpecV41ReturnObjResponse:
    masterOrderID: Optional[str]  # 主订单ID。调用方在拿到masterOrderID之后，可以使用masterOrderID进一步确认订单状态及资源状态
    masterOrderNO: Optional[str]  # 订单号
    regionID: Optional[str]  # 资源池ID，您可以查看<a href="https://www.ctyun.cn/document/10026730/10028695">地域和可用区</a>来了解资源池 <br />获取：<br /><span style="background-color: rgb(73, 204, 144);color: rgb(255,255,255);padding: 2px; margin:2px">查</span> <a  href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=5851&data=87">资源池列表查询</a>




    @staticmethod
    def from_json(json_data: dict) -> 'CtecsUpdateFlavorSpecV41ReturnObjResponse':
        if not json_data:
            return None
        obj = CtecsUpdateFlavorSpecV41ReturnObjResponse(
            masterOrderID=json_data.get('masterOrderID'),
            masterOrderNO=json_data.get('masterOrderNO'),
            regionID=json_data.get('regionID')
        )
        return obj

@dataclass
class CtecsUpdateFlavorSpecV41Response:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str]  # 业务细分码，为product.module.code三段式码，详见错误码部分
    error: Optional[str]  # 错误码，为product.module.code三段式码，详见错误码部分  
    message: Optional[str]  # 英文描述信息
    description: Optional[str]  # 中文描述信息
    returnObj: Optional[CtecsUpdateFlavorSpecV41ReturnObjResponse]  # 成功时返回的数据

    @staticmethod
    def from_json(json_data: dict) -> 'CtecsUpdateFlavorSpecV41Response':
        if not json_data:
            return None
        return_obj = None
        if 'returnObj' in json_data and json_data['returnObj']:
            return_obj = CtecsUpdateFlavorSpecV41ReturnObjResponse.from_json(json_data['returnObj'])

        obj = CtecsUpdateFlavorSpecV41Response(
            statusCode=json_data.get('statusCode'),
            errorCode=json_data.get('errorCode'),
            error=json_data.get('error'),
            message=json_data.get('message'),
            description=json_data.get('description'),
            returnObj=return_obj
        )
        return obj


# 支持对一台处于关机状态的云主机进行规格变更<br /><b>准备工作</b>：<br />&emsp;&emsp;构造请求：在调用前需要了解如何构造请求，详情查看<a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=%u6784%u9020%u8BF7%u6C42&data=87&vid=81">构造请求</a><br />&emsp;&emsp;认证鉴权：openapi请求需要进行加密调用，详细查看<a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=%u8BA4%u8BC1%u9274%u6743&data=87&vid=81">认证鉴权</a><br /><b>注意事项：</b><br/>&emsp;&emsp;成本估算：了解云主机的<a href="https://www.ctyun.cn/document/10026730/10028700">计费项</a><br/>&emsp;&emsp;异步接口：该接口为异步接口，下单成功不代表业务成功<br />&emsp;&emsp;代金券：只支持预付费用户抵扣包周期资源的金额，且不可超过包周期资源的金额
class CtecsUpdateFlavorSpecV41Api:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtecsUpdateFlavorSpecV41Request) -> CtecsUpdateFlavorSpecV41Response:
        url = endpoint + "/v4/ecs/update-flavor-spec"

        try:
            request_dict = request.to_dict()
            response = client.post(url=url, data=request_dict, credential=credential)
            return CtecsUpdateFlavorSpecV41Response.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
