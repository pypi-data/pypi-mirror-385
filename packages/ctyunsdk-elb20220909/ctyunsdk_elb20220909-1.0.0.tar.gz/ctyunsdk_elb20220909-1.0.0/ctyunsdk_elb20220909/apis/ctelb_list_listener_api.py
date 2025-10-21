from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbListListenerRequest:
    clientToken: Optional[str]  # 客户端存根，用于保证订单幂等性。要求单个云平台账户内唯一, 公共参数不支持修改, 长度 1 - 64
    regionID: str  # 区域ID
    projectID: Optional[str]  # 企业项目ID，默认为'0'
    iDs: Optional[str]  # 监听器ID列表，以','分隔
    name: Optional[str]  # 监听器名称
    loadBalancerID: Optional[str]  # 负载均衡实例ID
    accessControlID: Optional[str]  # 访问控制ID


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbListListenerRequest':
        if not json_data:
            return None
        obj = CtelbListListenerRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbListListenerReturnObjDefaultActionForwardConfigTargetGroupsResponse:
    targetGroupID: Optional[str]  # 后端服务组ID
    weight: Any  # 权重


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbListListenerReturnObjDefaultActionForwardConfigTargetGroupsResponse':
        if not json_data:
            return None
        obj = CtelbListListenerReturnObjDefaultActionForwardConfigTargetGroupsResponse(None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbListListenerReturnObjDefaultActionForwardConfigResponse:
    targetGroups: Optional[List[Optional[CtelbListListenerReturnObjDefaultActionForwardConfigTargetGroupsResponse]]]  # 后端服务组


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbListListenerReturnObjDefaultActionForwardConfigResponse':
        if not json_data:
            return None
        obj = CtelbListListenerReturnObjDefaultActionForwardConfigResponse(None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbListListenerReturnObjDefaultActionResponse:
    type: Optional[str]  # 默认规则动作类型: forward / redirect
    forwardConfig: Optional[List[Optional[CtelbListListenerReturnObjDefaultActionForwardConfigResponse]]]  # 转发配置
    redirectListenerID: Optional[str]  # 重定向监听器ID


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbListListenerReturnObjDefaultActionResponse':
        if not json_data:
            return None
        obj = CtelbListListenerReturnObjDefaultActionResponse(None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbListListenerReturnObjResponse:
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
    defaultAction: Optional[List[Optional[CtelbListListenerReturnObjDefaultActionResponse]]]  # 默认规则动作
    accessControlID: Optional[str]  # 访问控制ID
    accessControlType: Optional[str]  # 访问控制类型: Close / White / Black
    forwardedForEnabled: Optional[bool]  # 是否开启x forward for功能
    status: Optional[str]  # 监听器状态: DOWN / ACTIVE
    createdTime: Optional[str]  # 创建时间，为UTC格式
    updatedTime: Optional[str]  # 更新时间，为UTC格式


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbListListenerReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbListListenerReturnObjResponse(None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbListListenerResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[List[Optional[CtelbListListenerReturnObjResponse]]]  # 接口业务数据


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbListListenerResponse':
        if not json_data:
            return None
        obj = CtelbListListenerResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 查看监听器列表
class CtelbListListenerApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbListListenerRequest) -> CtelbListListenerResponse:
        url = endpoint + "/v4/elb/list-listener"
        params = {'clientToken':request.clientToken, 'regionID':request.regionID, 'projectID':request.projectID, 'iDs':request.iDs, 'name':request.name, 'loadBalancerID':request.loadBalancerID, 'accessControlID':request.accessControlID}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtelbListListenerResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
