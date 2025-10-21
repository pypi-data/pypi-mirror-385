from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbIplistenerShowRequest:
    regionID: str  # 资源池 ID
    ipListenerID: str  # 监听器 ID


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbIplistenerShowRequest':
        if not json_data:
            return None
        obj = CtelbIplistenerShowRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbIplistenerShowReturnObjActionForwardConfigResponse:
    """转发配置"""
    targetGroups: Optional[str]  # 后端服务组


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbIplistenerShowReturnObjActionForwardConfigResponse':
        if not json_data:
            return None
        obj = CtelbIplistenerShowReturnObjActionForwardConfigResponse(None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbIplistenerShowReturnObjActionResponse:
    """转发配置"""
    type: Optional[str]  # 默认规则动作类型: forward / redirect
    forwardConfig: Optional[CtelbIplistenerShowReturnObjActionForwardConfigResponse]  # 转发配置


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbIplistenerShowReturnObjActionResponse':
        if not json_data:
            return None
        obj = CtelbIplistenerShowReturnObjActionResponse(None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbIplistenerShowReturnObjResponse:
    """接口业务数据"""
    gwElbID: Optional[str]  # 网关负载均衡 ID
    name: Optional[str]  # 名字
    description: Optional[str]  # 描述
    ipListenerID: Optional[str]  # 监听器 id
    action: Optional[CtelbIplistenerShowReturnObjActionResponse]  # 转发配置


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbIplistenerShowReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbIplistenerShowReturnObjResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbIplistenerShowResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtelbIplistenerShowReturnObjResponse]  # 接口业务数据


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbIplistenerShowResponse':
        if not json_data:
            return None
        obj = CtelbIplistenerShowResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 查看ip_listener详情
class CtelbIplistenerShowApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbIplistenerShowRequest) -> CtelbIplistenerShowResponse:
        url = endpoint + "/v4/iplistener/show"
        params = {'regionID':request.regionID, 'ipListenerID':request.ipListenerID}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtelbIplistenerShowResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
