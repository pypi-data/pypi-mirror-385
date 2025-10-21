from typing import List, Optional, Dict, Any
from ctyunsdk_vpc20220909.core.client import CtyunClient
from ctyunsdk_vpc20220909.core.credential import Credential
from ctyunsdk_vpc20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcUnbindHavipRequest:
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 资源池ID
    resourceType: str  # 绑定的实例类型，VM 表示虚拟机ECS, PM 表示裸金属, NETWORK 表示弹性 IP
    haVipID: str  # 高可用虚IP的ID
    networkInterfaceID: Optional[str] = None # 虚拟网卡ID = None
    instanceID: Optional[str] = None # ECS示例ID，当 resourceType 为 VM / PM 时，必填 = None
    floatingID: Optional[str] = None # 弹性IP ID，当 resourceType 为 NETWORK 时，必填 = None



@dataclass_json
@dataclass
class CtvpcUnbindHavipReturnObjResponse:
    """解绑状态"""
    status: Optional[str]  # 解绑状态，取值 in_progress / done
    message: Optional[str]  # 绑定状态提示信息


@dataclass_json
@dataclass
class CtvpcUnbindHavipResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtvpcUnbindHavipReturnObjResponse]  # 解绑状态



# 将 HaVip 从 ECS 实例上解绑，由于绑定是异步操作，在第一次请求后，并不会立即返回解绑结果，调用者在获取到解绑状态为 in_progress 时，继续使用相同参数进行请求，获取最新的解绑结果，直到最后的解绑状态为 done 即可停止请求。
class CtvpcUnbindHavipApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtvpcUnbindHavipRequest) -> CtvpcUnbindHavipResponse:
        url = endpoint + "/v4/vpc/havip/unbind"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtvpcUnbindHavipResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
