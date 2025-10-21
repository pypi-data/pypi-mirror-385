from typing import List, Optional, Dict, Any
from ctyunsdk_vpc20220909.core.client import CtyunClient
from ctyunsdk_vpc20220909.core.credential import Credential
from ctyunsdk_vpc20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcListSubnetRequest:
    regionID: str  # 资源池 ID
    pageNumber: Optional[Any] = None  # 列表的页码，默认值为 1。
    pageNo: Optional[Any] = None  # 列表的页码，默认值为 1, 推荐使用该字段, pageNumber 后续会废弃
    pageSize: Optional[Any] = None  # 分页查询时每页的行数，最大值为 200，默认值为 10。
    maxResults: Optional[Any] = None  # 最大数量
    clientToken: Optional[str] = None # 客户端存根，用于保证订单幂等性, 长度 1 - 64 = None
    vpcID: Optional[str] = None # VPC 的 ID = None
    subnetID: Optional[str] = None # 多个 subnet 的 ID 之间用半角逗号（,）隔开。 = None
    nextToken: Optional[str] = None # 下一页游标 = None



@dataclass_json
@dataclass
class CtvpcListSubnetReturnObjSubnetsResponse:
    subnetID: Optional[str]  # subnet ID
    name: Optional[str]  # 名称
    description: Optional[str]  # 描述
    vpcID: Optional[str]  # VpcID
    availabilityZones: Optional[List[Optional[str]]]  # 子网所在的可用区名
    routeTableID: Optional[str]  # 子网路由表 ID
    networkAclID: Optional[str]  # 子网 aclID
    CIDR: Optional[str]  # 子网网段，掩码范围为 16-28 位
    gatewayIP: Optional[str]  # 子网网关
    dhcpIP: Optional[str]  # dhcpIP
    start: Optional[str]  # 子网网段起始 IP
    end: Optional[str]  # 子网网段结束 IP
    availableIPCount: Any  # 子网内可用 IPv4 数目
    ipv6Enabled: Any  # 是否配置了ipv6网段
    enableIpv6: Optional[bool]  # 是否开启 ipv6
    ipv6CIDR: Optional[str]  # 子网 Ipv6 网段，掩码范围为 16-28 位
    ipv6Start: Optional[str]  # 子网内可用的起始 IPv6 地址
    ipv6End: Optional[str]  # 子网内可用的结束 IPv6 地址
    ipv6GatewayIP: Optional[str]  # v6 网关地址
    dnsList: Optional[List[Optional[str]]]  # DNS 服务器地址:默认为空；必须为正确的 IPv4 格式；重新触发 DHCP 后生效，最大数组长度为 4
    systemDnsList: Optional[List[Optional[str]]]  # 系统自带DNS服务器地址
    ntpList: Optional[List[Optional[str]]]  # NTP 服务器地址: 默认为空，必须为正确的域名或 IPv4 格式；重新触发 DHCP 后生效，最大数组长度为 4
    type: Any  # 子网类型 :当前仅支持：0（普通子网）, 1（裸金属子网）
    updateAt: Optional[str]  # 更新时间
    createAt: Optional[str]  # 创建时间
    projectID: Optional[str]  # 企业项目


@dataclass_json
@dataclass
class CtvpcListSubnetReturnObjResponse:
    """接口业务数据"""
    subnets: Optional[List[Optional[CtvpcListSubnetReturnObjSubnetsResponse]]]  # subnets 组


@dataclass_json
@dataclass
class CtvpcListSubnetResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtvpcListSubnetReturnObjResponse]  # 接口业务数据
    totalCount: Any  # 列表条目数
    currentCount: Any  # 分页查询时每页的行数。
    totalPage: Any  # 总页数



# 查询用户专有网络下子网列表
class CtvpcListSubnetApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtvpcListSubnetRequest) -> CtvpcListSubnetResponse:
        url = endpoint + "/v4/vpc/list-subnet"
        params = {'clientToken':request.clientToken, 'regionID':request.regionID, 'vpcID':request.vpcID, 'subnetID':request.subnetID, 'pageNumber':request.pageNumber, 'pageNo':request.pageNo, 'pageSize':request.pageSize, 'nextToken':request.nextToken, 'maxResults':request.maxResults}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtvpcListSubnetResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
