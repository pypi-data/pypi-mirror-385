from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbAsyncCreateTargetTargetsRequest:
    instanceID: str  # 后端服务主机 id
    protocolPort: Any  # 后端服务监听端口，1-65535
    instanceType: str  # 后端服务主机类型，仅支持vm类型
    weight: Any  # 后端服务主机权重: 1 - 256
    address: str  # 后端服务主机主网卡所在的 IP


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbAsyncCreateTargetTargetsRequest':
        if not json_data:
            return None
        obj = CtelbAsyncCreateTargetTargetsRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbAsyncCreateTargetRequest:
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 区域ID
    targetGroupID: str  # 后端服务组ID
    targets: List[CtelbAsyncCreateTargetTargetsRequest]  # 后端服务主机


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbAsyncCreateTargetRequest':
        if not json_data:
            return None
        obj = CtelbAsyncCreateTargetRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbAsyncCreateTargetReturnObjResponse:
    """返回结果"""
    pass  # 空类占位符

    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbAsyncCreateTargetReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbAsyncCreateTargetReturnObjResponse()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbAsyncCreateTargetResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtelbAsyncCreateTargetReturnObjResponse]  # 返回结果


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbAsyncCreateTargetResponse':
        if not json_data:
            return None
        obj = CtelbAsyncCreateTargetResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 创建后端服务
class CtelbAsyncCreateTargetApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbAsyncCreateTargetRequest) -> CtelbAsyncCreateTargetResponse:
        url = endpoint + "/v4/elb/async-create-vm"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtelbAsyncCreateTargetResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
