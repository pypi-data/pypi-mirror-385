from typing import List, Optional, Dict, Any
from ctyunsdk_vpc20220909.core.client import CtyunClient
from ctyunsdk_vpc20220909.core.credential import Credential
from ctyunsdk_vpc20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcVpcCreateSubnetRequest:
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 资源池 ID
    vpcID: str  # 虚拟私有云 ID
    name: str  # 支持拉丁字母、中文、数字，下划线，连字符，中文 / 英文字母开头，不能以 http: / https: 开头，长度 2 - 32
    CIDR: str  # 子网网段
    description: Optional[str] = None # 支持拉丁字母、中文、数字, 特殊字符：~!@#$%^&*()_-+= <>?:{},./;'[\]·！@#￥%……&*（） —— -+={}\|《》？：“”【】、；‘'，。、，不能以 http: / https: 开头，长度 0 - 128 = None
    enableIpv6: Optional[bool] = None # 是否开启 IPv6 网段。取值：false（默认值）:不开启，true: 开启 = None
    dnsList: Optional[List[Optional[str]]] = None # 子网 dns 列表, 最多同时支持 4 个 dns 地址 = None
    subnetGatewayIP: Optional[str] = None # 子网网关 IP = None
    subnetType: Optional[str] = None # 子网类型：common（普通子网）/ cbm（裸金属子网），默认为普通子网 = None
    dhcpIP: Optional[str] = None # dhcpIP,和网关IP不能相同 = None



@dataclass_json
@dataclass
class CtvpcVpcCreateSubnetReturnObjResponse:
    """接口业务数据"""
    subnetID: Optional[str]  # subnet 示例 ID


@dataclass_json
@dataclass
class CtvpcVpcCreateSubnetResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtvpcVpcCreateSubnetReturnObjResponse]  # 接口业务数据



# 创建子网。
class CtvpcVpcCreateSubnetApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtvpcVpcCreateSubnetRequest) -> CtvpcVpcCreateSubnetResponse:
        url = endpoint + "/v4/vpc/create-subnet"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtvpcVpcCreateSubnetResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
