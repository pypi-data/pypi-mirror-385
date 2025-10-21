from typing import List, Optional, Dict, Any
from ctyunsdk_eip20220909.core.client import CtyunClient
from ctyunsdk_eip20220909.core.credential import Credential
from ctyunsdk_eip20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcCheckEipAddressRequest:
    regionID: str  # 资源池 ID
    eipAddress: str  # 弹性公网IP地址
    clientToken: Optional[str] = None  # 客户端存根，用于保证订单幂等性, 长度 1 - 64


@dataclass_json
@dataclass
class CtvpcCheckEipAddressReturnObjResponse:
    """返回结果"""
    eipAddress: Optional[str] = None  # 弹性公网IP地址
    used: Optional[bool] = None  # 是否被使用


@dataclass_json
@dataclass
class CtvpcCheckEipAddressResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str] = None  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str] = None  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str] = None  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtvpcCheckEipAddressReturnObjResponse] = None  # 返回结果


# 调用此接口可检查弹性公网IP地址是否已经被使用。
class CtvpcCheckEipAddressApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)

    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint

    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str,
           request: CtvpcCheckEipAddressRequest) -> CtvpcCheckEipAddressResponse:
        url = endpoint + "/v4/eip/check-address"
        params = {'clientToken': request.clientToken, 'regionID': request.regionID, 'eipAddress': request.eipAddress}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtvpcCheckEipAddressResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
