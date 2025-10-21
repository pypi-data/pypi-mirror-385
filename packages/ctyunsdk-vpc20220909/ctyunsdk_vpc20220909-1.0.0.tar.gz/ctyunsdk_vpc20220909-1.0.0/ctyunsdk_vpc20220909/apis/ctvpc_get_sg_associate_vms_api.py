from typing import List, Optional, Dict, Any
from ctyunsdk_vpc20220909.core.client import CtyunClient
from ctyunsdk_vpc20220909.core.credential import Credential
from ctyunsdk_vpc20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcGetSgAssociateVmsRequest:
    regionID: str  # 区域id
    securityGroupID: str  # 安全组ID
    pageNo: Optional[Any] = None  # 列表的页码，默认值为 1, 推荐使用该字段, pageNumber 后续会废弃
    pageSize: Optional[Any] = None  # 分页查询时每页的行数，最大值为 50，默认值为 10



@dataclass_json
@dataclass
class CtvpcGetSgAssociateVmsReturnObjResultsResponse:
    instanceID: Optional[str]  # 主机 ID
    instanceName: Optional[str]  # 主机名
    instanceType: Optional[str]  # 主机类型：VM / BM
    instanceState: Optional[str]  # 主机状态
    privateIp: Optional[str]  # 私有 ipv4
    privateIpv6: Optional[str]  # 私有 ipv6


@dataclass_json
@dataclass
class CtvpcGetSgAssociateVmsReturnObjResponse:
    """返回结果"""
    results: Optional[List[Optional[CtvpcGetSgAssociateVmsReturnObjResultsResponse]]]  # 业务数据
    totalCount: Any  # 列表条目数
    currentCount: Any  # 分页查询时每页的行数。
    totalPage: Any  # 总页数


@dataclass_json
@dataclass
class CtvpcGetSgAssociateVmsResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtvpcGetSgAssociateVmsReturnObjResponse]  # 返回结果



# 获取安全组绑定机器列表
class CtvpcGetSgAssociateVmsApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtvpcGetSgAssociateVmsRequest) -> CtvpcGetSgAssociateVmsResponse:
        url = endpoint + "/v4/vpc/get-sg-associate-vms"
        params = {'regionID':request.regionID, 'securityGroupID':request.securityGroupID, 'pageNo':request.pageNo, 'pageSize':request.pageSize}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtvpcGetSgAssociateVmsResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
