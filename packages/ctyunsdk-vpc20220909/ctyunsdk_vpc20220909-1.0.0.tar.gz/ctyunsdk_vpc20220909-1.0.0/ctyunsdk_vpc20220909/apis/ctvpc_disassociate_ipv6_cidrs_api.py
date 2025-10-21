from typing import List, Optional, Dict, Any
from ctyunsdk_vpc20220909.core.client import CtyunClient
from ctyunsdk_vpc20220909.core.credential import Credential
from ctyunsdk_vpc20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcDisassociateIpv6CidrsRequest:
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 资源池ID
    vpcID: str  # vpc id
    ipv6CIDRs: List[str]  # 是Array类型，里面的内容是String，要解绑的ipv6 cidr



@dataclass_json
@dataclass
class CtvpcDisassociateIpv6CidrsResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    requestID: Optional[str]  # 请求 id



# VPC解绑Ipv6网段。
class CtvpcDisassociateIpv6CidrsApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtvpcDisassociateIpv6CidrsRequest) -> CtvpcDisassociateIpv6CidrsResponse:
        url = endpoint + "/v4/vpc/disassociate-ipv6-cidrs"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtvpcDisassociateIpv6CidrsResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
