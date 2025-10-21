from typing import List, Optional, Dict, Any
from ctyunsdk_vpc20220909.core.client import CtyunClient
from ctyunsdk_vpc20220909.core.credential import Credential
from ctyunsdk_vpc20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcCreateVpc1Request:
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 资源池 ID
    name: str  # 支持拉丁字母、中文、数字，下划线，连字符，中文 / 英文字母开头，不能以 http: / https: 开头，长度 2 - 32
    CIDR: str  # VPC 的网段。建议您使用 192.168.0.0/16、172.16.0.0/12、10.0.0.0/8 三个 RFC 标准私网网段及其子网作为专有网络的主 IPv4 网段，网段掩码有效范围为 8~28 位
    projectID: Optional[str] = None  # 企业项目 ID，默认为0
    description: Optional[
        str] = None  # 支持拉丁字母、中文、数字, 特殊字符：~!@#$%^&*()_-+= <>?:{},./;'[,]·！@#￥%……&*（） —— -+={},《》？：“”【】、；‘'，。、，不能以 http: / https: 开头，长度 0 - 128
    enableIpv6: Optional[bool] = None  # 是否开启 IPv6 网段。取值：false（默认值）:不开启，true: 开启
    ipv6SegmentPoolID: Optional[str] = None  # ipv6 segment pool id，当 addressPoolType = custom 时，必传
    addressPoolType: Optional[str] = None  # 地址类型：ctyun / custom
    ipv6Cidr: Optional[str] = None  # ipv6 地址段
    ipv6Isp: Optional[
        str] = None  # isp，支持 chinatelecom / chinaunicom / chinamobile / bgp-3 / pro-crossline，当 addressPoolType = ctyun 时，必传


@dataclass_json
@dataclass
class CtvpcCreateVpc1ReturnObjResponse:
    """接口业务数据"""
    vpcID: Optional[str]  # vpc 示例 ID
    createdAt: Optional[str]  # 创建时间
    updatedAt: Optional[str]  # 更新时间


@dataclass_json
@dataclass
class CtvpcCreateVpc1Response:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtvpcCreateVpc1ReturnObjResponse]  # 接口业务数据


# 创建一个专有网络VPC。
class CtvpcCreateVpc1Api:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)

    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint

    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str,
           request: CtvpcCreateVpc1Request) -> CtvpcCreateVpc1Response:
        url = endpoint + "/v4/vpc/create"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict,
                                   credential=credential)
            return CtvpcCreateVpc1Response.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
