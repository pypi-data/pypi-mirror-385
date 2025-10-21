from typing import List, Optional, Dict, Any
from ctyunsdk_vpc20220909.core.client import CtyunClient
from ctyunsdk_vpc20220909.core.credential import Credential
from ctyunsdk_vpc20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcCreateHavipRequest:
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 资源池ID
    subnetID: str  # 子网ID
    networkID: Optional[str] = None # VPC的ID = None
    ipAddress: Optional[str] = None # ip地址 = None
    vipType: Optional[str] = None # 虚拟IP的类型，v4-IPv4类型虚IP，v6-IPv6类型虚IP。默认为v4 = None
    description: Optional[str] = None # 支持拉丁字母、中文、数字, 特殊字符：~!@#$%^&*()_-+= <>?:'{},./;'[,]·！@#￥%……&*（） —— -+={},《》？：“”【】、；‘'，。、，不能以 http: / https: 开头，长度 0 - 128 = None



@dataclass_json
@dataclass
class CtvpcCreateHavipReturnObjResponse:
    """接口业务数据"""
    uuid: Optional[str]  # 高可用虚IP的ID
    ipv4: Optional[str]  # 高可用虚IP的地址
    ipv6: Optional[str]  # 高可用虚IP的地址


@dataclass_json
@dataclass
class CtvpcCreateHavipResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtvpcCreateHavipReturnObjResponse]  # 接口业务数据



# 创建高可用虚IP
class CtvpcCreateHavipApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtvpcCreateHavipRequest) -> CtvpcCreateHavipResponse:
        url = endpoint + "/v4/vpc/havip/create"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtvpcCreateHavipResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
