from typing import List, Optional, Dict, Any
from ctyunsdk_vpc20220909.core.client import CtyunClient
from ctyunsdk_vpc20220909.core.credential import Credential
from ctyunsdk_vpc20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcNewACLListRequest:
    regionID: str  # 资源池ID
    pageNumber: Optional[Any] = None  # 列表的页码，默认值为1
    pageNo: Optional[Any] = None  # 列表的页码，默认值为 1, 推荐使用该字段, pageNumber 后续会废弃
    pageSize: Optional[Any] = None  # 分页查询时每页的行数，最大值为 50，默认值为 10
    aclID: Optional[str] = None # aclID = None
    name: Optional[str] = None # acl Name = None



@dataclass_json
@dataclass
class CtvpcNewACLListReturnObjAclsResponse:
    aclID: Optional[str]  # acl id
    name: Optional[str]  # acl 名称
    description: Optional[str]  # 描述
    applyToPublicLb: Optional[bool]  # 是否启用acl管控lb流量
    vpcID: Optional[str]  # 虚拟私有云 id
    enabled: Optional[str]  # 是否启用，取值范围：disable,enable
    inPolicyID: Optional[List[Optional[str]]]  # 入规则id数组
    outPolicyID: Optional[List[Optional[str]]]  # 出规则id数组 
    createdAt: Optional[str]  # 创建时间
    updatedAt: Optional[str]  # 更新时间
    subnetIDs: Optional[List[Optional[str]]]  # acl 绑定的子网 id


@dataclass_json
@dataclass
class CtvpcNewACLListReturnObjResponse:
    """接口业务数据"""
    acls: Optional[List[Optional[CtvpcNewACLListReturnObjAclsResponse]]]  # acl 规则列表
    totalCount: Any  # 列表条目数。
    currentCount: Any  # 分页查询时每页的行数。
    totalPage: Any  # 分页查询时总页数。


@dataclass_json
@dataclass
class CtvpcNewACLListResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    requestID: Optional[str]  # 请求 id
    returnObj: Optional[CtvpcNewACLListReturnObjResponse]  # 接口业务数据



# 查看 Acl 列表信息
class CtvpcNewACLListApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtvpcNewACLListRequest) -> CtvpcNewACLListResponse:
        url = endpoint + "/v4/acl/new-list"
        params = {'regionID':request.regionID, 'aclID':request.aclID, 'name':request.name, 'pageNumber':request.pageNumber, 'pageNo':request.pageNo, 'pageSize':request.pageSize}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtvpcNewACLListResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
