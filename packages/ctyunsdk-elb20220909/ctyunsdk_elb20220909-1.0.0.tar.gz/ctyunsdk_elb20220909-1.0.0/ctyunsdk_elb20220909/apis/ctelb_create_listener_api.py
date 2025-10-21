from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbCreateListenerDefaultActionForwardConfigTargetGroupsRequest:
    targetGroupID: str  # 后端服务组ID
    weight: Any  # 后端主机权重，取值范围：1-256。默认为100


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbCreateListenerDefaultActionForwardConfigTargetGroupsRequest':
        if not json_data:
            return None
        obj = CtelbCreateListenerDefaultActionForwardConfigTargetGroupsRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbCreateListenerDefaultActionForwardConfigRequest:
    """转发配置，当type为forward时，此字段必填"""
    targetGroups: List[CtelbCreateListenerDefaultActionForwardConfigTargetGroupsRequest]  # 后端服务组


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbCreateListenerDefaultActionForwardConfigRequest':
        if not json_data:
            return None
        obj = CtelbCreateListenerDefaultActionForwardConfigRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbCreateListenerDefaultActionRequest:
    """默认规则动作"""
    type: str  # 默认规则动作类型。取值范围：forward、redirect
    forwardConfig: Optional[CtelbCreateListenerDefaultActionForwardConfigRequest]  # 转发配置，当type为forward时，此字段必填
    redirectListenerID: Optional[str]  # 重定向监听器ID，当type为redirect时，此字段必填


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbCreateListenerDefaultActionRequest':
        if not json_data:
            return None
        obj = CtelbCreateListenerDefaultActionRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbCreateListenerRequest:
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 区域ID
    loadBalancerID: str  # 负载均衡实例ID
    name: str  # 唯一。支持拉丁字母、中文、数字，下划线，连字符，中文 / 英文字母开头，不能以 http: / https: 开头，长度 2 - 32
    description: Optional[str]  # 支持拉丁字母、中文、数字, 特殊字符：~!@#$%^&*()_-+= <>?:{},./;'[]·！@#￥%……&*（） —— -+={}\|《》？：“”【】、；‘'，。、，不能以 http: / https: 开头，长度 0 - 128
    protocol: str  # 监听协议。取值范围：TCP、UDP、HTTP、HTTPS
    protocolPort: Any  # 负载均衡实例监听端口。取值：1-65535
    certificateID: Optional[str]  # 证书ID。当protocol为HTTPS时,此参数必选
    caEnabled: Optional[bool]  # 是否开启双向认证。false（不开启）、true（开启）
    clientCertificateID: Optional[str]  # 双向认证的证书ID
    defaultAction: CtelbCreateListenerDefaultActionRequest  # 默认规则动作
    accessControlID: Optional[str]  # 访问控制ID
    accessControlType: Optional[str]  # 访问控制类型。取值范围：Close（未启用）、White（白名单）、Black（黑名单）
    forwardedForEnabled: Optional[bool]  # x forward for功能。false（未开启）、true（开启）


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbCreateListenerRequest':
        if not json_data:
            return None
        obj = CtelbCreateListenerRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbCreateListenerReturnObjResponse:
    iD: Optional[str]  # 监听器 ID


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbCreateListenerReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbCreateListenerReturnObjResponse(None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbCreateListenerResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[List[Optional[CtelbCreateListenerReturnObjResponse]]]  # 返回结果


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbCreateListenerResponse':
        if not json_data:
            return None
        obj = CtelbCreateListenerResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 创建监听器
class CtelbCreateListenerApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbCreateListenerRequest) -> CtelbCreateListenerResponse:
        url = endpoint + "/v4/elb/create-listener"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtelbCreateListenerResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
