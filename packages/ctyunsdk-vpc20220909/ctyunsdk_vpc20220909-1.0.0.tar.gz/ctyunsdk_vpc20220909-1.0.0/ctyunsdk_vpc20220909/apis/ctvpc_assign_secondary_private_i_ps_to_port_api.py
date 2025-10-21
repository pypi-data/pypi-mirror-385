from typing import List, Optional, Dict, Any
from ctyunsdk_vpc20220909.core.client import CtyunClient
from ctyunsdk_vpc20220909.core.credential import Credential
from ctyunsdk_vpc20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass_json
@dataclass_json
@dataclass
class CtvpcAssignSecondaryPrivateIPsToPortRequest:
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 资源池ID
    networkInterfaceID: str  # 弹性网卡ID
    secondaryPrivateIpCount: Any  # 辅助私网IP数量，新增自动分配辅助私网IP的数量, 最多支持 15 个
    secondaryPrivateIps: Optional[List[Optional[str]]] = None # 辅助私网IP列表，新增辅助私网IP, 最多支持 15 个 = None



@dataclass_json
@dataclass
class CtvpcAssignSecondaryPrivateIPsToPortReturnObjResponse:
    """业务数据"""
    secondaryPrivateIps: Optional[List[Optional[str]]]  # 分配的私网 ip 地址


@dataclass_json
@dataclass
class CtvpcAssignSecondaryPrivateIPsToPortResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtvpcAssignSecondaryPrivateIPsToPortReturnObjResponse]  # 业务数据



# 网卡关联辅助私网IP
class CtvpcAssignSecondaryPrivateIPsToPortApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtvpcAssignSecondaryPrivateIPsToPortRequest) -> CtvpcAssignSecondaryPrivateIPsToPortResponse:
        url = endpoint + "/v4/ports/assign-secondary-private-ips"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtvpcAssignSecondaryPrivateIPsToPortResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
