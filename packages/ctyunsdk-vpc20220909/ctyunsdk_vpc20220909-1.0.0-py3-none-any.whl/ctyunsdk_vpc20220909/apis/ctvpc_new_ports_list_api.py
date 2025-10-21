from typing import List, Optional, Dict, Any
from ctyunsdk_vpc20220909.core.client import CtyunClient
from ctyunsdk_vpc20220909.core.credential import Credential
from ctyunsdk_vpc20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcNewPortsListRequest:
    regionID: str  # 区域id
    pageNumber: Optional[Any] = None  # 列表的页码，默认值为 1。
    pageNo: Optional[Any] = None  # 列表的页码，默认值为 1, 推荐使用该字段, pageNumber 后续会废弃
    pageSize: Optional[Any] = None  # 分页查询时每页的行数，最大值为 50，默认值为 10。
    maxResults: Optional[Any] = None  # 最大分页数
    vpcID: Optional[str] = None # 所属vpc id = None
    deviceID: Optional[str] = None # 关联设备id = None
    subnetID: Optional[str] = None # 所属子网id = None
    nextToken: Optional[str] = None # 下一页游标 = None



@dataclass_json
@dataclass
class CtvpcNewPortsListReturnObjPortsResponse:
    networkInterfaceName: Optional[str]  # 虚拟网名称
    networkInterfaceID: Optional[str]  # 虚拟网id
    vpcID: Optional[str]  # 所属vpc
    subnetID: Optional[str]  # 所属子网id
    role: Any  # 网卡类型: 0 主网卡， 1 弹性网卡
    macAddress: Optional[str]  # mac地址
    primaryPrivateIp: Optional[str]  # 主ip
    ipv6Addresses: Optional[List[Optional[str]]]  # ipv6地址
    instanceID: Optional[str]  # 关联的设备id
    instanceType: Optional[str]  # 设备类型 VM(云主机), BM(裸金属), LB(弹性负载均衡), CBM(标准裸金属)
    description: Optional[str]  # 描述
    securityGroupIds: Optional[List[Optional[str]]]  # 安全组ID列表
    secondaryPrivateIps: Optional[List[Optional[str]]]  # 辅助私网IP
    adminStatus: Optional[str]  # 是否启用DOWN, UP


@dataclass_json
@dataclass
class CtvpcNewPortsListReturnObjResponse:
    """接口业务数据"""
    ports: Optional[List[Optional[CtvpcNewPortsListReturnObjPortsResponse]]]  # 网卡列表
    totalCount: Any  # 列表条目数
    currentCount: Any  # 分页查询时每页的行数。
    totalPage: Any  # 总页数


@dataclass_json
@dataclass
class CtvpcNewPortsListResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtvpcNewPortsListReturnObjResponse]  # 接口业务数据



# 弹性网卡列表
class CtvpcNewPortsListApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtvpcNewPortsListRequest) -> CtvpcNewPortsListResponse:
        url = endpoint + "/v4/ports/new-list"
        params = {'regionID':request.regionID, 'vpcID':request.vpcID, 'deviceID':request.deviceID, 'subnetID':request.subnetID, 'pageNumber':request.pageNumber, 'pageNo':request.pageNo, 'pageSize':request.pageSize, 'nextToken':request.nextToken, 'maxResults':request.maxResults}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtvpcNewPortsListResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
