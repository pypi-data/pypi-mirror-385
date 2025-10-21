from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbGwlbListTargetGroupRequest:
    regionID: str  # 资源池 ID
    targetGroupID: Optional[str]  # 后端服务组 ID
    pageNumber: Any  # 列表的页码，默认值为 1。
    pageSize: Any  # 分页查询时每页的行数，最大值为 50，默认值为 10。


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbGwlbListTargetGroupRequest':
        if not json_data:
            return None
        obj = CtelbGwlbListTargetGroupRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbGwlbListTargetGroupReturnObjResultsResponse:
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
    def from_json(json_data: dict) -> 'CtelbGwlbListTargetGroupReturnObjResultsResponse':
        if not json_data:
            return None
        obj = CtelbGwlbListTargetGroupReturnObjResultsResponse(None,None,None,None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbGwlbListTargetGroupReturnObjResponse:
    """接口业务数据"""
    results: Optional[List[Optional[CtelbGwlbListTargetGroupReturnObjResultsResponse]]]  # 接口业务数据
    totalCount: Any  # 列表条目数
    currentCount: Any  # 分页查询时每页的行数。
    totalPage: Any  # 总页数


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbGwlbListTargetGroupReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbGwlbListTargetGroupReturnObjResponse(None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbGwlbListTargetGroupResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtelbGwlbListTargetGroupReturnObjResponse]  # 接口业务数据


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbGwlbListTargetGroupResponse':
        if not json_data:
            return None
        obj = CtelbGwlbListTargetGroupResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 查看target_group列表
class CtelbGwlbListTargetGroupApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbGwlbListTargetGroupRequest) -> CtelbGwlbListTargetGroupResponse:
        url = endpoint + "/v4/gwlb/list-target-group"
        params = {'regionID':request.regionID, 'targetGroupID':request.targetGroupID, 'pageNumber':request.pageNumber, 'pageSize':request.pageSize}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtelbGwlbListTargetGroupResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
