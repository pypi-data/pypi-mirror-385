from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbShowListenerRequest:
    regionID: str  # 区域ID
    iD: Optional[str]  # 监听器ID, 该字段后续废弃
    listenerID: str  # 监听器ID, 推荐使用该字段, 当同时使用 ID 和 listenerID 时，优先使用 listenerID


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbShowListenerRequest':
        if not json_data:
            return None
        obj = CtelbShowListenerRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbShowListenerReturnObjDefaultActionForwardConfigResponse:
    """转发配置"""
    targetGroups: Optional[str]  # 后端服务组


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbShowListenerReturnObjDefaultActionForwardConfigResponse':
        if not json_data:
            return None
        obj = CtelbShowListenerReturnObjDefaultActionForwardConfigResponse(None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbShowListenerReturnObjDefaultActionResponse:
    type: Optional[str]  # 默认规则动作类型: forward / redirect
    forwardConfig: Optional[CtelbShowListenerReturnObjDefaultActionForwardConfigResponse]  # 转发配置
    redirectListenerID: Optional[str]  # 重定向监听器ID


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbShowListenerReturnObjDefaultActionResponse':
        if not json_data:
            return None
        obj = CtelbShowListenerReturnObjDefaultActionResponse(None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbShowListenerReturnObjResponse:
    regionID: Optional[str]  # 区域ID
    azName: Optional[str]  # 可用区名称
    projectID: Optional[str]  # 项目ID
    iD: Optional[str]  # 监听器ID
    name: Optional[str]  # 监听器名称
    description: Optional[str]  # 描述
    loadBalancerID: Optional[str]  # 负载均衡实例ID
    protocol: Optional[str]  # 监听协议: TCP / UDP / HTTP / HTTPS
    protocolPort: Any  # 监听端口
    certificateID: Optional[str]  # 证书ID
    caEnabled: Optional[bool]  # 是否开启双向认证
    clientCertificateID: Optional[str]  # 双向认证的证书ID
    defaultAction: Optional[List[Optional[CtelbShowListenerReturnObjDefaultActionResponse]]]  # 默认规则动作
    accessControlID: Optional[str]  # 访问控制ID
    accessControlType: Optional[str]  # 访问控制类型: Close / White / Black
    forwardedForEnabled: Optional[bool]  # 是否开启x forward for功能
    status: Optional[str]  # 监听器状态: DOWN / ACTIVE
    createdTime: Optional[str]  # 创建时间，为UTC格式
    updatedTime: Optional[str]  # 更新时间，为UTC格式


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbShowListenerReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbShowListenerReturnObjResponse(None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbShowListenerResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[List[Optional[CtelbShowListenerReturnObjResponse]]]  # 接口业务数据


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbShowListenerResponse':
        if not json_data:
            return None
        obj = CtelbShowListenerResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 查看监听器详情
class CtelbShowListenerApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbShowListenerRequest) -> CtelbShowListenerResponse:
        url = endpoint + "/v4/elb/show-listener"
        params = {'regionID':request.regionID, 'iD':request.iD, 'listenerID':request.listenerID}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtelbShowListenerResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
