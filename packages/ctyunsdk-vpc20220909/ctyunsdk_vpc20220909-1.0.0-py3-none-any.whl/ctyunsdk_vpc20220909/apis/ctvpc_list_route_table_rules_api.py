from typing import List, Optional, Dict, Any
from ctyunsdk_vpc20220909.core.client import CtyunClient
from ctyunsdk_vpc20220909.core.credential import Credential
from ctyunsdk_vpc20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcListRouteTableRulesRequest:
    regionID: str  # 区域id
    routeTableID: str  # 路由表 id
    pageNumber: Optional[Any] = None  # 列表的页码，默认值为 1。
    pageNo: Optional[Any] = None  # 列表的页码，默认值为 1, 推荐使用该字段, pageNumber 后续会废弃
    pageSize: Optional[Any] = None  # 分页查询时每页的行数，最大值为 50，默认值为 10。



@dataclass_json
@dataclass
class CtvpcListRouteTableRulesReturnObjResponse:
    nextHopID: Optional[str]  # 下一跳设备 id
    nextHopType: Optional[str]  # vpcpeering / havip / bm / vm / natgw/ igw6 / dc / ticc / vpngw / enic
    destination: Optional[str]  # 无类别域间路由
    ipVersion: Any  # 4 表示 ipv4, 6 表示 ipv6
    description: Optional[str]  # 规则描述
    routeRuleID: Optional[str]  # 路由规则 id


@dataclass_json
@dataclass
class CtvpcListRouteTableRulesResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    totalCount: Any  # 列表条目数
    currentCount: Any  # 分页查询时每页的行数。
    totalPage: Any  # 总页数
    returnObj: Optional[List[Optional[CtvpcListRouteTableRulesReturnObjResponse]]]  # 返回结果



# 查询路由表规则列表
class CtvpcListRouteTableRulesApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtvpcListRouteTableRulesRequest) -> CtvpcListRouteTableRulesResponse:
        url = endpoint + "/v4/vpc/route-table/list-rules"
        params = {'regionID':request.regionID, 'routeTableID':request.routeTableID, 'pageNumber':request.pageNumber, 'pageNo':request.pageNo, 'pageSize':request.pageSize}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtvpcListRouteTableRulesResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
