from typing import List, Optional, Dict, Any
from ctyunsdk_eip20220909.core.client import CtyunClient
from ctyunsdk_eip20220909.core.credential import Credential
from ctyunsdk_eip20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcEipBandwidthUtilizationRequest:
    regionID: str  # 资源池 ID
    eipID: str  # 弹性公网IP的ID


@dataclass_json
@dataclass
class CtvpcEipBandwidthUtilizationReturnObjResponse:
    """返回结果"""
    ingressBandwidthUtilization: Optional[str] = None  # 入方向带宽利用率
    egressBandwidthUtilization: Optional[str] = None  # 出方向带宽利用率


@dataclass_json
@dataclass
class CtvpcEipBandwidthUtilizationResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str] = None  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str] = None  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str] = None  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtvpcEipBandwidthUtilizationReturnObjResponse] = None  # 返回结果


# eip带宽利用率
class CtvpcEipBandwidthUtilizationApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)

    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint

    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str,
           request: CtvpcEipBandwidthUtilizationRequest) -> CtvpcEipBandwidthUtilizationResponse:
        url = endpoint + "/v4/eip/bandwidth-utilization"
        params = {'regionID': request.regionID, 'eipID': request.eipID}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtvpcEipBandwidthUtilizationResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
