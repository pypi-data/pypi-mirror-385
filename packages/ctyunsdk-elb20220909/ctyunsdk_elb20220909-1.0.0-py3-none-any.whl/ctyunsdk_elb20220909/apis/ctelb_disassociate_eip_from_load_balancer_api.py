from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbDisassociateEipFromLoadBalancerRequest:
    clientToken: Optional[str]  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 区域ID
    iD: Optional[str]  # 负载均衡ID, 该字段后续废弃
    elbID: str  # 负载均衡ID, 推荐使用该字段, 当同时使用 ID 和 elbID 时，优先使用 elbID
    eipID: str  # 弹性公网IP的ID


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbDisassociateEipFromLoadBalancerRequest':
        if not json_data:
            return None
        obj = CtelbDisassociateEipFromLoadBalancerRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbDisassociateEipFromLoadBalancerReturnObjResponse:
    iD: Optional[str]  # 负载均衡ID


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbDisassociateEipFromLoadBalancerReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbDisassociateEipFromLoadBalancerReturnObjResponse(None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbDisassociateEipFromLoadBalancerResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[List[Optional[CtelbDisassociateEipFromLoadBalancerReturnObjResponse]]]  # 返回结果


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbDisassociateEipFromLoadBalancerResponse':
        if not json_data:
            return None
        obj = CtelbDisassociateEipFromLoadBalancerResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 解绑弹性 IP
class CtelbDisassociateEipFromLoadBalancerApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbDisassociateEipFromLoadBalancerRequest) -> CtelbDisassociateEipFromLoadBalancerResponse:
        url = endpoint + "/v4/elb/disassociate-eip-from"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtelbDisassociateEipFromLoadBalancerResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
