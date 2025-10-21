from typing import List, Optional, Dict, Any
from ctyunsdk_vpc20220909.core.client import CtyunClient
from ctyunsdk_vpc20220909.core.credential import Credential
from ctyunsdk_vpc20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcV4PortsAsyncAttachBmRequest:
    regionID: str  # 资源池ID
    azName: str  # 可用区
    networkInterfaceID: str  # 网卡ID
    instanceID: str  # 绑定实例ID



@dataclass_json
@dataclass
class CtvpcV4PortsAsyncAttachBmReturnObjResponse:
    """数据详细信息"""
    status: Optional[str]  # 状态。in_progress表示在异步处理中，done表示成功


@dataclass_json
@dataclass
class CtvpcV4PortsAsyncAttachBmResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtvpcV4PortsAsyncAttachBmReturnObjResponse]  # 数据详细信息



# 网卡绑定物理机
class CtvpcV4PortsAsyncAttachBmApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtvpcV4PortsAsyncAttachBmRequest) -> CtvpcV4PortsAsyncAttachBmResponse:
        url = endpoint + "/v4/ports/async-attach-bm"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtvpcV4PortsAsyncAttachBmResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
