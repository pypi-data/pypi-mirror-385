from typing import List, Optional, Dict, Any
from ctyunsdk_vpc20220909.core.client import CtyunClient
from ctyunsdk_vpc20220909.core.credential import Credential
from ctyunsdk_vpc20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcReplaceSubnetRouteTableRequest:
    regionID: str  # 资源池 ID
    subnetID: str  # 子网 的 ID
    routeTableID: str  # 路由表的 ID
    clientToken: Optional[str] = None # 客户端存根，用于保证订单幂等性, 长度 1 - 64 = None



@dataclass_json
@dataclass
class CtvpcReplaceSubnetRouteTableResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS



# 子网更换路由表，子网必须关联一张路由表。创建VPC后会自动生成一张默认路由表，新建子网时，会关联到默认路由表，子网可以更换其他路由表。
class CtvpcReplaceSubnetRouteTableApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtvpcReplaceSubnetRouteTableRequest) -> CtvpcReplaceSubnetRouteTableResponse:
        url = endpoint + "/v4/vpc/replace-subnet-route-table"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtvpcReplaceSubnetRouteTableResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
