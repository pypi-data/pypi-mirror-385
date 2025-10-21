from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbCreateRuleActionForwardConfigTargetGroupsRequest:
    targetGroupID: str  # 后端服务组ID
    weight: Any  # 权重，取值范围：1-256。默认为100


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbCreateRuleActionForwardConfigTargetGroupsRequest':
        if not json_data:
            return None
        obj = CtelbCreateRuleActionForwardConfigTargetGroupsRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbCreateRuleActionForwardConfigRequest:
    """转发配置"""
    targetGroups: Optional[List[Optional[CtelbCreateRuleActionForwardConfigTargetGroupsRequest]]]  # 后端服务组


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbCreateRuleActionForwardConfigRequest':
        if not json_data:
            return None
        obj = CtelbCreateRuleActionForwardConfigRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbCreateRuleConditionsUrlPathConfigRequest:
    """匹配路径"""
    urlPaths: Optional[str]  # 匹配路径
    matchType: Optional[str]  # 匹配类型。取值范围：ABSOLUTE，PREFIX，REG


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbCreateRuleConditionsUrlPathConfigRequest':
        if not json_data:
            return None
        obj = CtelbCreateRuleConditionsUrlPathConfigRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbCreateRuleConditionsServerNameConfigRequest:
    """服务名称"""
    serverName: Optional[str]  # 服务名称


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbCreateRuleConditionsServerNameConfigRequest':
        if not json_data:
            return None
        obj = CtelbCreateRuleConditionsServerNameConfigRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbCreateRuleActionRequest:
    """规则目标"""
    type: str  # 默认规则动作类型。取值范围：forward、redirect、deny(目前暂不支持配置为deny)
    forwardConfig: Optional[CtelbCreateRuleActionForwardConfigRequest]  # 转发配置
    redirectListenerID: Optional[str]  # 重定向监听器ID，当type为redirect时，此字段必填


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbCreateRuleActionRequest':
        if not json_data:
            return None
        obj = CtelbCreateRuleActionRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbCreateRuleConditionsRequest:
    type: str  # 类型。取值范围：server_name（服务名称）、url_path（匹配路径）
    serverNameConfig: Optional[CtelbCreateRuleConditionsServerNameConfigRequest]  # 服务名称
    urlPathConfig: Optional[CtelbCreateRuleConditionsUrlPathConfigRequest]  # 匹配路径


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbCreateRuleConditionsRequest':
        if not json_data:
            return None
        obj = CtelbCreateRuleConditionsRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbCreateRuleRequest:
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 区域ID
    listenerID: str  # 监听器ID
    priority: Any  # 优先级，数字越小优先级越高，取值范围为：1-100(目前不支持配置此参数,只取默认值100)
    description: Optional[str]  # 支持拉丁字母、中文、数字, 特殊字符：~!@#$%^&*()_-+= <>?:'{},./;'[,]·！@#￥%……&*（） —— -+={},《》？：“”【】、；‘'，。、，不能以 http: / https: 开头，长度 0 - 128
    conditions: List[CtelbCreateRuleConditionsRequest]  # 匹配规则数据
    action: CtelbCreateRuleActionRequest  # 规则目标


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbCreateRuleRequest':
        if not json_data:
            return None
        obj = CtelbCreateRuleRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbCreateRuleReturnObjResponse:
    iD: Optional[str]  # 转发规则 ID


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbCreateRuleReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbCreateRuleReturnObjResponse(None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbCreateRuleResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[List[Optional[CtelbCreateRuleReturnObjResponse]]]  # 返回结果


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbCreateRuleResponse':
        if not json_data:
            return None
        obj = CtelbCreateRuleResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 创建转发规则
class CtelbCreateRuleApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbCreateRuleRequest) -> CtelbCreateRuleResponse:
        url = endpoint + "/v4/elb/create-rule"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtelbCreateRuleResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
