from typing import List, Optional, Dict, Any
from ctyunsdk_vpc20220909.core.client import CtyunClient
from ctyunsdk_vpc20220909.core.credential import Credential
from ctyunsdk_vpc20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcNewRouteTableListRequest:
    regionID: str  # 区域id
    type: Any  # 路由表类型:0-子网路由表；2-网关路由表
    pageNumber: Optional[Any] = None  # 列表的页码，默认值为 1。
    pageNo: Optional[Any] = None  # 列表的页码，默认值为 1, 推荐使用该字段, pageNumber 后续会废弃
    pageSize: Optional[Any] = None  # 分页查询时每页的行数，最大值为 50，默认值为 10。
    vpcID: Optional[str] = None # 关联的vpcID = None
    queryContent: Optional[str] = None # 对路由表名字 / 路由表描述 / 路由表 id 进行模糊查询 = None
    routeTableID: Optional[str] = None # 路由表 id = None



@dataclass_json
@dataclass
class CtvpcNewRouteTableListReturnObjRouteTablesResponse:
    name: Optional[str]  # 路由表名字
    description: Optional[str]  # 路由表描述
    vpcID: Optional[str]  # 虚拟私有云 id
    id: Optional[str]  # 路由 id
    freezing: Optional[bool]  # 是否冻结
    routeRulesCount: Any  # 路由表中的路由数
    createdAt: Optional[str]  # 创建时间
    updatedAt: Optional[str]  # 更新时间
    type: Any  # 路由表类型:0-子网路由表，2-网关路由表
    origin: Optional[str]  # 路由表来源：default-系统默认; user-用户创建


@dataclass_json
@dataclass
class CtvpcNewRouteTableListReturnObjResponse:
    """返回结果"""
    routeTables: Optional[List[Optional[CtvpcNewRouteTableListReturnObjRouteTablesResponse]]]  # 路由列表
    totalCount: Any  # 列表条目数
    currentCount: Any  # 分页查询时每页的行数。
    totalPage: Any  # 总页数


@dataclass_json
@dataclass
class CtvpcNewRouteTableListResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtvpcNewRouteTableListReturnObjResponse]  # 返回结果



# 查询路由表列表
class CtvpcNewRouteTableListApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtvpcNewRouteTableListRequest) -> CtvpcNewRouteTableListResponse:
        url = endpoint + "/v4/vpc/route-table/new-list"
        params = {'regionID':request.regionID, 'vpcID':request.vpcID, 'queryContent':request.queryContent, 'routeTableID':request.routeTableID, 'type':request.type, 'pageNumber':request.pageNumber, 'pageNo':request.pageNo, 'pageSize':request.pageSize}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtvpcNewRouteTableListResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
