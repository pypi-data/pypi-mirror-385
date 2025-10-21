from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbGwlbListTargetRequest:
    regionID: str  # 资源池 ID
    targetGroupID: str  # 后端服务组 ID
    targetID: Optional[str]  # 后端服务 ID
    pageNumber: Any  # 列表的页码，默认值为 1。
    pageSize: Any  # 分页查询时每页的行数，最大值为 50，默认值为 10。


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbGwlbListTargetRequest':
        if not json_data:
            return None
        obj = CtelbGwlbListTargetRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbGwlbListTargetReturnObjResultsResponse:
    targetID: Optional[str]  # 后端服务ID
    targetGroupID: Optional[str]  # 后端服务组ID
    instanceType: Optional[str]  # 实例类型，取值有: VM / BMS/ CBM
    instanceID: Optional[str]  # 实例 ID
    instanceVpc: Optional[str]  # 实例所在的 vpc
    weight: Any  # 权重
    healthCheckStatus: Optional[str]  # ipv4 健康检查状态，取值: unknown / online / offline
    healthCheckStatusIpv6: Optional[str]  # ipv6 健康检查状态，取值: unknown / online / offline
    createdAt: Optional[str]  # 创建时间
    updatedAt: Optional[str]  # 更新时间


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbGwlbListTargetReturnObjResultsResponse':
        if not json_data:
            return None
        obj = CtelbGwlbListTargetReturnObjResultsResponse(None,None,None,None,None,None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbGwlbListTargetReturnObjResponse:
    """接口业务数据"""
    results: Optional[List[Optional[CtelbGwlbListTargetReturnObjResultsResponse]]]  # 接口业务数据
    totalCount: Any  # 列表条目数
    currentCount: Any  # 分页查询时每页的行数。
    totalPage: Any  # 总页数


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbGwlbListTargetReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbGwlbListTargetReturnObjResponse(None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbGwlbListTargetResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtelbGwlbListTargetReturnObjResponse]  # 接口业务数据


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbGwlbListTargetResponse':
        if not json_data:
            return None
        obj = CtelbGwlbListTargetResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 查看target列表
class CtelbGwlbListTargetApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbGwlbListTargetRequest) -> CtelbGwlbListTargetResponse:
        url = endpoint + "/v4/gwlb/list-target"
        params = {'regionID':request.regionID, 'targetGroupID':request.targetGroupID, 'targetID':request.targetID, 'pageNumber':request.pageNumber, 'pageSize':request.pageSize}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtelbGwlbListTargetResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
