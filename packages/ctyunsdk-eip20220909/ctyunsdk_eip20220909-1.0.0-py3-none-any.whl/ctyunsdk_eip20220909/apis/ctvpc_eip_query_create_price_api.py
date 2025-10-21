from typing import List, Optional, Dict, Any
from ctyunsdk_eip20220909.core.client import CtyunClient
from ctyunsdk_eip20220909.core.credential import Credential
from ctyunsdk_eip20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcEipQueryCreatePriceRequest:
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 资源池 ID
    cycleType: str  # 订购类型：month（包月） / year（包年） / on_demand（按需）
    name: str  # 弹性 IP 名称
    cycleCount: Optional[
        Any] = None  # 订购时长, 当 cycleType = month, 支持续订 1 - 11 个月; 当 cycleType = year, 支持续订 1 - 3 年, 当 cycleType = on_demand 时，可以不传
    bandwidth: Optional[Any] = None  # 弹性 IP 的带宽峰值，默认为 1 Mbps,1-300
    bandwidthID: Optional[str] = None  # 当 cycleType 为 on_demand 时，可以使用 bandwidthID，将弹性 IP 加入到共享带宽中
    demandBillingType: Optional[str] = None  # 按需计费类型，当 cycleType 为 on_demand 时必填，支持 bandwidth（按带宽）/ upflowc（按流量）


@dataclass_json
@dataclass
class CtvpcEipQueryCreatePriceReturnObjSubOrderPricesOrderItemPricesResponse:
    resourceType: Optional[str] = None  # 资源类型
    totalPrice: Optional[Any] = None  # 总价格（单位：元）
    finalPrice: Optional[Any] = None  # 最终价格（单位：元）


@dataclass_json
@dataclass
class CtvpcEipQueryCreatePriceReturnObjSubOrderPricesResponse:
    serviceTag: Optional[str] = None  # 服务类型
    totalPrice: Optional[Any] = None  # 子订单总价格（单位：元）
    finalPrice: Optional[Any] = None  # 最终价格（单位：元）
    orderItemPrices: Optional[
        List[Optional[CtvpcEipQueryCreatePriceReturnObjSubOrderPricesOrderItemPricesResponse]]] = None  # item价格信息


@dataclass_json
@dataclass
class CtvpcEipQueryCreatePriceReturnObjResponse:
    """业务数据"""
    totalPrice: Optional[Any] = None  # 总价格（单位：元）
    discountPrice: Optional[Any] = None  # 折后价格（单位：元）
    finalPrice: Optional[Any] = None  # 最终价格（单位：元）
    subOrderPrices: Optional[List[Optional[CtvpcEipQueryCreatePriceReturnObjSubOrderPricesResponse]]] = None  # 子订单价格信息


@dataclass_json
@dataclass
class CtvpcEipQueryCreatePriceResponse:
    statusCode: Optional[Any] = None  # 返回状态码（800为成功，900为失败）
    message: Optional[str] = None  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str] = None  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str] = None  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtvpcEipQueryCreatePriceReturnObjResponse] = None  # 业务数据


# 创建询价。
class CtvpcEipQueryCreatePriceApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)

    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint

    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str,
           request: CtvpcEipQueryCreatePriceRequest) -> CtvpcEipQueryCreatePriceResponse:
        url = endpoint + "/v4/eip/query-create-price"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict,
                                   credential=credential)
            return CtvpcEipQueryCreatePriceResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
