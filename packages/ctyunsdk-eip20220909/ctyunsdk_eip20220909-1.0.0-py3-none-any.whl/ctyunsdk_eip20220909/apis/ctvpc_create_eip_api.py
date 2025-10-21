from typing import List, Optional, Dict, Any
from ctyunsdk_eip20220909.core.client import CtyunClient
from ctyunsdk_eip20220909.core.credential import Credential
from ctyunsdk_eip20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcCreateEipRequest:
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 资源池 ID
    cycleType: str  # 订购类型：month（包月） / year（包年） / on_demand（按需）
    name: str  # 支持拉丁字母、中文、数字，下划线，连字符，中文 / 英文字母开头，不能以 http: / https: 开头，长度 2 - 32
    bandwidth: Any  # 弹性 IP 的带宽峰值，默认为 1 Mbps
    cycleCount: Optional[Any] = None  # 订购时长, 当 cycleType = month, 支持续订 1 - 11 个月; 当 cycleType = year, 支持续订 1 - 3 年, 当 cycleType = on_demand 时，可以不传
    projectID: Optional[str] = None  # 不填默认为默认企业项目，如果需要指定企业项目，则需要填写
    bandwidthID: Optional[str] = None  # 当 cycleType 为 on_demand 时，可以使用 bandwidthID，将弹性 IP 加入到共享带宽中
    demandBillingType: Optional[str] = None  # 按需计费类型，当 cycleType 为 on_demand 时生效，支持 bandwidth（按带宽）/ upflowc（按流量）
    payVoucherPrice: Optional[str] = None  # 代金券金额，支持到小数点后两位，仅包周期支持代金券
    lineType: Optional[str] = None  # 线路类型，默认为163，支持163 / bgp / chinamobile / chinaunicom
    segmentID: Optional[str] = None  # 专属地址池 segment id，先通过接口 /v4/eip/own-segments 获取
    exclusiveName: Optional[str] = None  # 专属地址池 exclusiveName, 先通过接口 /v4/eip/own-segments 获取


@dataclass_json
@dataclass
class CtvpcCreateEipReturnObjResponse:
    """返回结果"""
    masterOrderID: Optional[str] = None  # 订单id。
    masterOrderNO: Optional[str] = None  # 订单编号, 可以为 null。
    masterResourceStatus: Optional[str] = None
    # 资源状态: started（启用） / renewed（续订） / refunded（退订） / destroyed（销毁） / failed（失败） / starting（正在启用） / changed（变配）/ expired（过期）/ unknown（未知）
    masterResourceID: Optional[str] = None  # 可以为 null。
    regionID: Optional[str] = None  # 可用区id。
    eipID: Optional[str] = None  # 弹性 IP id


@dataclass_json
@dataclass
class CtvpcCreateEipResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str] = None  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str] = None  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    returnObj: Optional[CtvpcCreateEipReturnObjResponse] = None  # 返回结果
    errorCode: Optional[str] = None  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS

    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtvpcCreateEipResponse':
        if not json_data:
            return None
        obj = CtvpcCreateEipResponse(None, None, None, None, None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 调用此接口可创建弹性公网IP（Elastic IP Address，简称EIP）。
class CtvpcCreateEipApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)

    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint

    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str,
           request: CtvpcCreateEipRequest) -> CtvpcCreateEipResponse:
        url = endpoint + "/v4/eip/create"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict,
                                   credential=credential)
            return CtvpcCreateEipResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
