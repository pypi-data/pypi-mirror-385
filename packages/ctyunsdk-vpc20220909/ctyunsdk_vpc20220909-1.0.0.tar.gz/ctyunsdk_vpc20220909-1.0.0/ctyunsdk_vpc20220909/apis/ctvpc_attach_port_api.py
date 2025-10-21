from typing import List, Optional, Dict, Any
from ctyunsdk_vpc20220909.core.client import CtyunClient
from ctyunsdk_vpc20220909.core.credential import Credential
from ctyunsdk_vpc20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcAttachPortRequest:
    clientToken: str  # 客户端存根，用于保证订单幂等性。要求当个云平台账户内唯一
    regionID: str  # 资源池ID
    azName: str  # 可用区
    networkInterfaceID: str  # 网卡ID
    instanceID: str  # 绑定实例ID
    instanceType: Any  # 实例类型：3-虚拟机



@dataclass_json
@dataclass
class CtvpcAttachPortResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS



# 网卡绑定实例
class CtvpcAttachPortApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtvpcAttachPortRequest) -> CtvpcAttachPortResponse:
        url = endpoint + "/v4/ports/attach"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtvpcAttachPortResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
