from typing import List, Optional, Dict, Any
from ctyunsdk_eip20220909.core.client import CtyunClient
from ctyunsdk_eip20220909.core.credential import Credential
from ctyunsdk_eip20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcGetEipFilingStatusRequest:
    regionID: str  # 资源池 ID
    eipID: str  # 弹性公网IP的ID


@dataclass_json
@dataclass
class CtvpcGetEipFilingStatusReturnObjResponse:
    """object"""
    accessControl: Optional[bool] = None  # 端口备案状态, true表示开启, false 表示关闭


@dataclass_json
@dataclass
class CtvpcGetEipFilingStatusResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str] = None  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str] = None  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str] = None  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtvpcGetEipFilingStatusReturnObjResponse] = None  # object


# 获取EIP端口备案状态。
class CtvpcGetEipFilingStatusApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)

    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint

    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str,
           request: CtvpcGetEipFilingStatusRequest) -> CtvpcGetEipFilingStatusResponse:
        url = endpoint + "/v4/eip/get-filing-status"
        params = {'regionID': request.regionID, 'eipID': request.eipID}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtvpcGetEipFilingStatusResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
