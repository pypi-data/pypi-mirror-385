from typing import List, Optional, Dict, Any
from ctyunsdk_vpc20220909.core.client import CtyunClient
from ctyunsdk_vpc20220909.core.credential import Credential
from ctyunsdk_vpc20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcListSecurityGroupsRequest:
    regionID: str  # 区域id
    pageNumber: Optional[Any] = None  # 列表的页码，默认值为 1。
    pageNo: Optional[Any] = None  # 列表的页码，默认值为 1, 推荐使用该字段, pageNumber 后续会废弃
    pageSize: Optional[Any] = None  # 分页查询时每页的行数，最大值为 50，默认值为 10。
    maxResults: Optional[Any] = None  # 最大数量
    vpcID: Optional[str] = None # 安全组所在的专有网络ID。 = None
    queryContent: Optional[str] = None # 【模糊查询】  安全组ID或名称 = None
    projectID: Optional[str] = None # 企业项目 ID，默认为0 = None
    instanceID: Optional[str] = None # 实例 ID = None
    nextToken: Optional[str] = None # 下一页游标 = None



@dataclass_json
@dataclass
class CtvpcListSecurityGroupsReturnObjSecurityGroupRuleListResponse:
    direction: Optional[str]  # 出方向-egress、入方向-ingress
    priority: Any  # 优先级:0~100
    ethertype: Optional[str]  # IP类型:IPv4、IPv6
    protocol: Optional[str]  # 协议: ANY、TCP、UDP、ICMP、ICMP6
    range: Optional[str]  # 接口范围/ICMP类型:1-65535
    destCidrIp: Optional[str]  # 远端地址:0.0.0.0/0
    description: Optional[str]  # 安全组规则描述信息。
    createTime: Optional[str]  # 创建时间，UTC时间。
    id: Optional[str]  # 唯一标识ID
    securityGroupID: Optional[str]  # 安全组ID
    action: Optional[str]  # 拒绝策略:允许-accept 拒绝-drop
    origin: Optional[str]  # 类型
    remoteSecurityGroupID: Optional[str]  # 远端安全组id
    prefixListID: Optional[str]  # 前缀列表id


@dataclass_json
@dataclass
class CtvpcListSecurityGroupsReturnObjResponse:
    securityGroupName: Optional[str]  # 安全组名称
    id: Optional[str]  # 安全组id
    vmNum: Any  # 相关云主机，该字段已经废弃，废弃后返回 0
    origin: Optional[str]  # 表示是否是默认安全组
    vpcName: Optional[str]  # vpc名称
    vpcID: Optional[str]  # 安全组所属的专有网络。
    creationTime: Optional[str]  # 创建时间
    description: Optional[str]  # 安全组描述信息。
    securityGroupRuleList: Optional[List[Optional[CtvpcListSecurityGroupsReturnObjSecurityGroupRuleListResponse]]]  # 安全组规则信息


@dataclass_json
@dataclass
class CtvpcListSecurityGroupsResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    totalCount: Any  # 列表条目数
    currentCount: Any  # 分页查询时每页的行数。
    totalPage: Any  # 总页数
    returnObj: Optional[List[Optional[CtvpcListSecurityGroupsReturnObjResponse]]]  # 返回结果



# 查询用户安全组列表。
class CtvpcListSecurityGroupsApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtvpcListSecurityGroupsRequest) -> CtvpcListSecurityGroupsResponse:
        url = endpoint + "/v4/vpc/query-security-groups"
        params = {'regionID':request.regionID, 'vpcID':request.vpcID, 'queryContent':request.queryContent, 'projectID':request.projectID, 'instanceID':request.instanceID, 'pageNumber':request.pageNumber, 'pageNo':request.pageNo, 'pageSize':request.pageSize, 'nextToken':request.nextToken, 'maxResults':request.maxResults}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtvpcListSecurityGroupsResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
