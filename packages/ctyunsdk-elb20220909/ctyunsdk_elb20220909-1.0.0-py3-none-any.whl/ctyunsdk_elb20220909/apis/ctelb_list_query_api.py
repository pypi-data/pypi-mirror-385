from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbListQueryRequest:
    regionID: str  # 区域ID
    iDs: Optional[str]  # 转发规则ID列表，以,分隔
    loadBalancerID: Optional[str]  # 负载均衡实例ID


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbListQueryRequest':
        if not json_data:
            return None
        obj = CtelbListQueryRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbListQueryReturnObjActionForwardConfigTargetGroupsResponse:
    targetGroupID: Optional[str]  # 后端服务组ID
    weight: Any  # 权重


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbListQueryReturnObjActionForwardConfigTargetGroupsResponse':
        if not json_data:
            return None
        obj = CtelbListQueryReturnObjActionForwardConfigTargetGroupsResponse(None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbListQueryReturnObjActionForwardConfigResponse:
    """转发配置"""
    targetGroups: Optional[List[Optional[CtelbListQueryReturnObjActionForwardConfigTargetGroupsResponse]]]  # 后端服务组


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbListQueryReturnObjActionForwardConfigResponse':
        if not json_data:
            return None
        obj = CtelbListQueryReturnObjActionForwardConfigResponse(None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbListQueryReturnObjConditionsUrlPathConfigResponse:
    """匹配路径"""
    urlPaths: Optional[str]  # 匹配路径
    matchType: Optional[str]  # 匹配类型。取值范围：ABSOLUTE，PREFIX，REG


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbListQueryReturnObjConditionsUrlPathConfigResponse':
        if not json_data:
            return None
        obj = CtelbListQueryReturnObjConditionsUrlPathConfigResponse(None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbListQueryReturnObjConditionsServerNameConfigResponse:
    """服务名称"""
    serverName: Optional[str]  # 服务名称


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbListQueryReturnObjConditionsServerNameConfigResponse':
        if not json_data:
            return None
        obj = CtelbListQueryReturnObjConditionsServerNameConfigResponse(None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbListQueryReturnObjActionResponse:
    """规则目标"""
    type: Optional[str]  # 默认规则动作类型
    forwardConfig: Optional[CtelbListQueryReturnObjActionForwardConfigResponse]  # 转发配置
    redirectListenerID: Optional[str]  # 重定向监听器ID


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbListQueryReturnObjActionResponse':
        if not json_data:
            return None
        obj = CtelbListQueryReturnObjActionResponse(None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbListQueryReturnObjConditionsResponse:
    type: Optional[str]  # 类型。取值范围：server_name（服务名称）、url_path（匹配路径）
    serverNameConfig: Optional[CtelbListQueryReturnObjConditionsServerNameConfigResponse]  # 服务名称
    urlPathConfig: Optional[CtelbListQueryReturnObjConditionsUrlPathConfigResponse]  # 匹配路径


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbListQueryReturnObjConditionsResponse':
        if not json_data:
            return None
        obj = CtelbListQueryReturnObjConditionsResponse(None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbListQueryReturnObjResponse:
    regionID: Optional[str]  # 区域ID
    azName: Optional[str]  # 可用区名称
    projectID: Optional[str]  # 项目ID
    iD: Optional[str]  # 转发规则ID
    loadBalancerID: Optional[str]  # 负载均衡ID
    listenerID: Optional[str]  # 监听器ID
    priority: Any  # 优先级
    description: Optional[str]  # 描述
    conditions: Optional[List[Optional[CtelbListQueryReturnObjConditionsResponse]]]  # 匹配规则数据
    action: Optional[CtelbListQueryReturnObjActionResponse]  # 规则目标
    status: Optional[str]  # 状态: ACTIVE / DOWN
    createdTime: Optional[str]  # 创建时间，为UTC格式
    updatedTime: Optional[str]  # 更新时间，为UTC格式


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbListQueryReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbListQueryReturnObjResponse(None,None,None,None,None,None,None,None,None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbListQueryResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[List[Optional[CtelbListQueryReturnObjResponse]]]  # 接口业务数据


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbListQueryResponse':
        if not json_data:
            return None
        obj = CtelbListQueryResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 获取转发规则列表
class CtelbListQueryApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbListQueryRequest) -> CtelbListQueryResponse:
        url = endpoint + "/v4/elb/list-rule"
        params = {'regionID':request.regionID, 'iDs':request.iDs, 'loadBalancerID':request.loadBalancerID}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtelbListQueryResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
