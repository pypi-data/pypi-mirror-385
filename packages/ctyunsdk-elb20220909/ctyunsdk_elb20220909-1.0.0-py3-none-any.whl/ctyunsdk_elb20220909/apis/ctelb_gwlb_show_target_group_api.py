from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbGwlbShowTargetGroupRequest:
    regionID: str  # 资源池 ID
    targetGroupID: str  # 后端服务组 ID


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbGwlbShowTargetGroupRequest':
        if not json_data:
            return None
        obj = CtelbGwlbShowTargetGroupRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbGwlbShowTargetGroupReturnObjResponse:
    """接口业务数据"""
    targetGroupID: Optional[str]  # 后端服务组ID
    name: Optional[str]  # 名称
    description: Optional[str]  # 描述
    vpcID: Optional[str]  # vpc id
    healthCheckID: Optional[str]  # 健康检查 ID
    failoverType: Any  # 故障转移类型
    bypassType: Any  # 旁路类型
    sessionStickyMode: Any  # 流保持类型,0:五元组, 4:二元组, 5:三元组


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbGwlbShowTargetGroupReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbGwlbShowTargetGroupReturnObjResponse(None,None,None,None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbGwlbShowTargetGroupResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtelbGwlbShowTargetGroupReturnObjResponse]  # 接口业务数据


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbGwlbShowTargetGroupResponse':
        if not json_data:
            return None
        obj = CtelbGwlbShowTargetGroupResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 查看target_group详情
class CtelbGwlbShowTargetGroupApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbGwlbShowTargetGroupRequest) -> CtelbGwlbShowTargetGroupResponse:
        url = endpoint + "/v4/gwlb/show-target-group"
        params = {'regionID':request.regionID, 'targetGroupID':request.targetGroupID}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtelbGwlbShowTargetGroupResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
