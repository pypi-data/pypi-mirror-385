from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbShowRuleRequest:
    regionID: str  # 区域ID
    iD: Optional[str]  # 转发规则ID, 该字段后续废弃
    policyID: Optional[str]  # 转发规则ID, 推荐使用该字段, 当同时使用 ID 和 policyID 时，优先使用 policyID


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbShowRuleRequest':
        if not json_data:
            return None
        obj = CtelbShowRuleRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbShowRuleReturnObjActionForwardConfigTargetGroupsResponse:
    targetGroupID: Optional[str]  # 后端服务组ID
    weight: Any  # 权重


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbShowRuleReturnObjActionForwardConfigTargetGroupsResponse':
        if not json_data:
            return None
        obj = CtelbShowRuleReturnObjActionForwardConfigTargetGroupsResponse(None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbShowRuleReturnObjActionForwardConfigResponse:
    """转发配置"""
    targetGroups: Optional[List[Optional[CtelbShowRuleReturnObjActionForwardConfigTargetGroupsResponse]]]  # 后端服务组


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbShowRuleReturnObjActionForwardConfigResponse':
        if not json_data:
            return None
        obj = CtelbShowRuleReturnObjActionForwardConfigResponse(None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbShowRuleReturnObjConditionsUrlPathConfigResponse:
    """匹配路径"""
    urlPaths: Optional[str]  # 匹配路径
    matchType: Optional[str]  # 匹配类型。取值范围：ABSOLUTE，PREFIX，REG


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbShowRuleReturnObjConditionsUrlPathConfigResponse':
        if not json_data:
            return None
        obj = CtelbShowRuleReturnObjConditionsUrlPathConfigResponse(None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbShowRuleReturnObjConditionsServerNameConfigResponse:
    """服务名称"""
    serverName: Optional[str]  # 服务名称


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbShowRuleReturnObjConditionsServerNameConfigResponse':
        if not json_data:
            return None
        obj = CtelbShowRuleReturnObjConditionsServerNameConfigResponse(None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbShowRuleReturnObjActionResponse:
    """规则目标"""
    type: Optional[str]  # 默认规则动作类型: forward / redirect
    forwardConfig: Optional[CtelbShowRuleReturnObjActionForwardConfigResponse]  # 转发配置
    redirectListenerID: Optional[str]  # 重定向监听器ID


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbShowRuleReturnObjActionResponse':
        if not json_data:
            return None
        obj = CtelbShowRuleReturnObjActionResponse(None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbShowRuleReturnObjConditionsResponse:
    type: Optional[str]  # 类型。取值范围：server_name（服务名称）、url_path（匹配路径）
    serverNameConfig: Optional[CtelbShowRuleReturnObjConditionsServerNameConfigResponse]  # 服务名称
    urlPathConfig: Optional[CtelbShowRuleReturnObjConditionsUrlPathConfigResponse]  # 匹配路径


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbShowRuleReturnObjConditionsResponse':
        if not json_data:
            return None
        obj = CtelbShowRuleReturnObjConditionsResponse(None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbShowRuleReturnObjResponse:
    """接口业务数据"""
    regionID: Optional[str]  # 区域ID
    azName: Optional[str]  # 可用区名称
    projectID: Optional[str]  # 项目ID
    iD: Optional[str]  # 转发规则ID
    loadBalancerID: Optional[str]  # 负载均衡ID
    listenerID: Optional[str]  # 监听器ID
    priority: Any  # 优先级
    description: Optional[str]  # 描述
    conditions: Optional[List[Optional[CtelbShowRuleReturnObjConditionsResponse]]]  # 匹配规则数据
    action: Optional[CtelbShowRuleReturnObjActionResponse]  # 规则目标
    status: Optional[str]  # 状态: ACTIVE / DOWN
    createdTime: Optional[str]  # 创建时间，为UTC格式
    updatedTime: Optional[str]  # 更新时间，为UTC格式


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbShowRuleReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbShowRuleReturnObjResponse(None,None,None,None,None,None,None,None,None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbShowRuleResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtelbShowRuleReturnObjResponse]  # 接口业务数据


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbShowRuleResponse':
        if not json_data:
            return None
        obj = CtelbShowRuleResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 获取转发规则详情
class CtelbShowRuleApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbShowRuleRequest) -> CtelbShowRuleResponse:
        url = endpoint + "/v4/elb/show-rule"
        params = {'regionID':request.regionID, 'iD':request.iD, 'policyID':request.policyID}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtelbShowRuleResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
