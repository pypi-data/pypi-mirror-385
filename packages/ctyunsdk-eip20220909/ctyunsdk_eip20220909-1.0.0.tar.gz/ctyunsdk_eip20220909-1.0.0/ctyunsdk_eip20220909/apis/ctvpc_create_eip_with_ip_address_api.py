from typing import List, Optional, Dict, Any
from ctyunsdk_eip20220909.core.client import CtyunClient
from ctyunsdk_eip20220909.core.credential import Credential
from ctyunsdk_eip20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcCreateEipWithIpAddressRequest:
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 资源池 ID
    cycleType: str  # 订购类型：month（包月） / year（包年） / on_demand（按需）
    name: str  # 弹性 IP 名称
    ipAddress: str  # 合法的公网 IP
    projectID: Optional[str] = None  # 企业项目 ID，默认为'0'  
    cycleCount: Optional[
        Any] = None  # 订购时长, cycleType 是 on_demand 为可选，当 cycleType = month, 支持续订 1 - 11 个月; 当 cycleType = year, 支持续订 1 - 3 年
    bandwidth: Optional[Any] = None  # 弹性 IP 的带宽峰值，默认为 1 Mbps
    bandwidthID: Optional[str] = None  # 当 cycleType 为 on_demand 时，可以使用 bandwidthID，将弹性 IP 加入到共享带宽中
    demandBillingType: Optional[str] = None  # 按需计费类型，当 cycleType 为 on_demand 时生效，支持 bandwidth（按带宽）/ upflowc（按流量）
    lineType: Optional[str] = None  # 线路类型，默认为163，支持163 / bgp / chinamobile / chinaunicom
    payVoucherPrice: Optional[str] = None  # 代金券金额，支持到小数点后两位，仅包周期支持代金券
    segmentID: Optional[str] = None  # 专属地址池 segment id，先通过接口 /v4/eip/own-segments 获取
    exclusiveName: Optional[str] = None  # 专属地址池 exclusiveName，先通过接口 /v4/eip/own-segments 获取


@dataclass_json
@dataclass
class CtvpcCreateEipWithIpAddressReturnObjResponse:
    """object"""
    masterOrderID: Optional[str] = None  # 订单id。
    masterOrderNO: Optional[str] = None  # 订单编号, 可以为 null。
    masterResourceStatus: Optional[str] = None  # 资源状态。
    masterResourceID: Optional[str] = None  # 可以为 null。
    regionID: Optional[str] = None  # 可用区id。
    eipID: Optional[str] = None  # 当 masterResourceStatus 不为 started 时，该值可能为


@dataclass_json
@dataclass
class CtvpcCreateEipWithIpAddressResponse:
    statusCode: Optional[Any] = None  # 返回状态码（800为成功，900为失败）
    message: Optional[str] = None  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str] = None  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str] = None  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtvpcCreateEipWithIpAddressReturnObjResponse] = None  # object


# 调用此接口可创建指定 IP 地址的弹性公网IP（Elastic IP Address，简称EIP）。
class CtvpcCreateEipWithIpAddressApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)

    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint

    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str,
           request: CtvpcCreateEipWithIpAddressRequest) -> CtvpcCreateEipWithIpAddressResponse:
        url = endpoint + "/v4/eip/create-with-ipaddress"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict,
                                   credential=credential)
            return CtvpcCreateEipWithIpAddressResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
