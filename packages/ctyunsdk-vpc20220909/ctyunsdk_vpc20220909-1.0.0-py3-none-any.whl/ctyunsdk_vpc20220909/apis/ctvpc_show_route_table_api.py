from typing import List, Optional, Dict, Any
from ctyunsdk_vpc20220909.core.client import CtyunClient
from ctyunsdk_vpc20220909.core.credential import Credential
from ctyunsdk_vpc20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcShowRouteTableRequest:
    regionID: str  # 区域id
    routeTableID: str  # 路由表 id



@dataclass_json
@dataclass
class CtvpcShowRouteTableReturnObjSubnetDetailResponse:
    id: Optional[str]  # 路由下子网 id
    name: Optional[str]  # 路由下子网名字
    cidr: Optional[str]  # ipv4 无类别域间路由
    ipv6Cidr: Optional[str]  # ipv6 无类别域间路由


@dataclass_json
@dataclass
class CtvpcShowRouteTableReturnObjResponse:
    """返回结果"""
    name: Optional[str]  # 路由表名字
    description: Optional[str]  # 路由表描述
    vpcID: Optional[str]  # 虚拟私有云 id
    id: Optional[str]  # 路由 id
    freezing: Optional[bool]  # 是否冻结
    routeRulesCount: Any  # 路由表中的路由数
    createdAt: Optional[str]  # 创建时间
    updatedAt: Optional[str]  # 更新时间
    routeRules: Optional[List[Optional[str]]]  # 路由规则 id 列表
    subnetDetail: Optional[List[Optional[CtvpcShowRouteTableReturnObjSubnetDetailResponse]]]  # 子网配置详情
    type: Any  # 路由表类型:0-子网路由表，2-网关路由表
    origin: Optional[str]  # 路由表来源：default-系统默认; user-用户创建


@dataclass_json
@dataclass
class CtvpcShowRouteTableResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtvpcShowRouteTableReturnObjResponse]  # 返回结果



# 查询路由表详情
class CtvpcShowRouteTableApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtvpcShowRouteTableRequest) -> CtvpcShowRouteTableResponse:
        url = endpoint + "/v4/vpc/route-table/show"
        params = {'regionID':request.regionID, 'routeTableID':request.routeTableID}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtvpcShowRouteTableResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
