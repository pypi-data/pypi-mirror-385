from typing import List, Optional, Dict, Any
from ctyunsdk_vpc20220909.core.client import CtyunClient
from ctyunsdk_vpc20220909.core.credential import Credential
from ctyunsdk_vpc20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcListVpcRequest:
    regionID: str  # 资源池 ID
    pageNumber: Optional[Any] = None  # 列表的页码，默认值为 1。
    pageNo: Optional[Any] = None  # 列表的页码，默认值为 1, 推荐使用该字段, pageNumber 后续会废弃
    pageSize: Optional[Any] = None  # 分页查询时每页的行数，最大值为 200，默认值为 10。
    projectID: Optional[str] = None # 企业项目 ID，默认为0 = None
    vpcID: Optional[str] = None # 多个 VPC 的 ID 之间用半角逗号（,）隔开。 = None
    vpcName: Optional[str] = None # vpc 名字 = None



@dataclass_json
@dataclass
class CtvpcListVpcReturnObjVpcsResponse:
    vpcID: Optional[str]  # vpc 示例 ID
    name: Optional[str]  # 名称
    description: Optional[str]  # 描述
    CIDR: Optional[str]  # CIDR
    ipv6Enabled: Optional[bool]  # 是否开启 ipv6
    enableIpv6: Optional[bool]  # 是否开启 ipv6
    ipv6CIDRS: Optional[List[Optional[str]]]  # ipv6CIDRS
    subnetIDs: Optional[List[Optional[str]]]  # 子网 id 列表
    natGatewayIDs: Optional[List[Optional[str]]]  # 网关 id 列表
    secondaryCIDRS: Optional[List[Optional[str]]]  # 附加网段
    projectID: Optional[str]  # 企业项目 ID，默认为0
    dhcpOptionsSetID: Optional[str]  # VPC关联的dhcp选项集
    vni: Any  # vni
    createdAt: Optional[str]  # 创建时间
    updatedAt: Optional[str]  # 更新时间
    dnsHostnamesEnabled: Any  # 开启 dns host name 解析


@dataclass_json
@dataclass
class CtvpcListVpcReturnObjResponse:
    """接口业务数据"""
    vpcs: Optional[List[Optional[CtvpcListVpcReturnObjVpcsResponse]]]  # vpc 组


@dataclass_json
@dataclass
class CtvpcListVpcResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtvpcListVpcReturnObjResponse]  # 接口业务数据
    totalCount: Any  # 列表条目数
    currentCount: Any  # 分页查询时每页的行数。
    totalPage: Any  # 总页数



# 查询用户专有网络列表
class CtvpcListVpcApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtvpcListVpcRequest) -> CtvpcListVpcResponse:
        url = endpoint + "/v4/vpc/list"
        params = {'regionID':request.regionID, 'projectID':request.projectID, 'vpcID':request.vpcID, 'vpcName':request.vpcName, 'pageNumber':request.pageNumber, 'pageNo':request.pageNo, 'pageSize':request.pageSize}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtvpcListVpcResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
