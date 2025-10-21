from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbUpdateListenerDefaultActionForwardConfigTargetGroupsRequest:
    targetGroupID: str  # 后端服务组ID
    weight: Any  # 权重，取值范围：1-256。默认为100


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbUpdateListenerDefaultActionForwardConfigTargetGroupsRequest':
        if not json_data:
            return None
        obj = CtelbUpdateListenerDefaultActionForwardConfigTargetGroupsRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbUpdateListenerDefaultActionForwardConfigRequest:
    """转发配置，当type为forward时，此字段必填"""
    targetGroups: Optional[List[Optional[CtelbUpdateListenerDefaultActionForwardConfigTargetGroupsRequest]]]  # 后端服务组


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbUpdateListenerDefaultActionForwardConfigRequest':
        if not json_data:
            return None
        obj = CtelbUpdateListenerDefaultActionForwardConfigRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbUpdateListenerDefaultActionRequest:
    """默认规则动作"""
    type: str  # 默认规则动作类型。取值范围： forward、redirect、deny(目前暂不支持配置为deny)
    forwardConfig: Optional[CtelbUpdateListenerDefaultActionForwardConfigRequest]  # 转发配置，当type为forward时，此字段必填
    redirectListenerID: Optional[str]  # 重定向监听器ID，当type为redirect时，此字段必填


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbUpdateListenerDefaultActionRequest':
        if not json_data:
            return None
        obj = CtelbUpdateListenerDefaultActionRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbUpdateListenerRequest:
    clientToken: Optional[str]  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 区域ID
    iD: Optional[str]  # 监听器ID, 该字段后续废弃
    listenerID: str  # 监听器ID, 推荐使用该字段, 当同时使用 ID 和 listenerID 时，优先使用 listenerID
    name: Optional[str]  # 唯一。支持拉丁字母、中文、数字，下划线，连字符，中文 / 英文字母开头，不能以 http: / https: 开头，长度 2 - 32
    description: Optional[str]  # 支持拉丁字母、中文、数字, 特殊字符：~!@#$%^&*()_-+= <>?:{},./;'[]·！@#￥%……&*（） —— -+={}\|《》？：“”【】、；‘'，。、，不能以 http: / https: 开头，长度 0 - 128
    certificateID: Optional[str]  # 证书ID
    caEnabled: Optional[bool]  # 是否开启双向认证。false（不开启）、true（开启）
    clientCertificateID: Optional[str]  # 双向认证的证书ID，如果caEnabled为true,此项必填
    defaultAction: Optional[CtelbUpdateListenerDefaultActionRequest]  # 默认规则动作
    accessControlID: Optional[str]  # 访问控制ID,如果accessControlType有值，此项必填
    accessControlType: Optional[str]  # 访问控制类型。Close（未启用）、White（白名单）、Black（黑名单）
    forwardedForEnabled: Optional[bool]  # x forward for功能。false（未开启）、true（开）


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbUpdateListenerRequest':
        if not json_data:
            return None
        obj = CtelbUpdateListenerRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbUpdateListenerReturnObjResponse:
    iD: Optional[str]  # 监听器 ID


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbUpdateListenerReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbUpdateListenerReturnObjResponse(None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbUpdateListenerResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[List[Optional[CtelbUpdateListenerReturnObjResponse]]]  # 返回结果


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbUpdateListenerResponse':
        if not json_data:
            return None
        obj = CtelbUpdateListenerResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 更新监听器
class CtelbUpdateListenerApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbUpdateListenerRequest) -> CtelbUpdateListenerResponse:
        url = endpoint + "/v4/elb/update-listener"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtelbUpdateListenerResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
