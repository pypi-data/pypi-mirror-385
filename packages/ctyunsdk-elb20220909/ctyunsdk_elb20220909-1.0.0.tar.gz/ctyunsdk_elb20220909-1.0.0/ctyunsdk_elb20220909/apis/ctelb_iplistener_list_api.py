from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbIplistenerListRequest:
    regionID: str  # 资源池 ID
    ipListenerID: Optional[str]  # 监听器 ID
    pageNumber: Any  # 列表的页码，默认值为 1。
    pageSize: Any  # 分页查询时每页的行数，最大值为 50，默认值为 10。


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbIplistenerListRequest':
        if not json_data:
            return None
        obj = CtelbIplistenerListRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbIplistenerListReturnObjResultsActionForwardConfigResponse:
    """转发配置"""
    targetGroups: Optional[str]  # 后端服务组


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbIplistenerListReturnObjResultsActionForwardConfigResponse':
        if not json_data:
            return None
        obj = CtelbIplistenerListReturnObjResultsActionForwardConfigResponse(None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbIplistenerListReturnObjResultsActionResponse:
    """转发配置"""
    type: Optional[str]  # 默认规则动作类型: forward / redirect
    forwardConfig: Optional[CtelbIplistenerListReturnObjResultsActionForwardConfigResponse]  # 转发配置


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbIplistenerListReturnObjResultsActionResponse':
        if not json_data:
            return None
        obj = CtelbIplistenerListReturnObjResultsActionResponse(None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbIplistenerListReturnObjResultsResponse:
    gwElbID: Optional[str]  # 网关负载均衡 ID
    name: Optional[str]  # 名字
    description: Optional[str]  # 描述
    ipListenerID: Optional[str]  # 监听器 id
    action: Optional[CtelbIplistenerListReturnObjResultsActionResponse]  # 转发配置


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbIplistenerListReturnObjResultsResponse':
        if not json_data:
            return None
        obj = CtelbIplistenerListReturnObjResultsResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbIplistenerListReturnObjResponse:
    """接口业务数据"""
    results: Optional[List[Optional[CtelbIplistenerListReturnObjResultsResponse]]]  # 接口业务数据
    totalCount: Any  # 列表条目数
    currentCount: Any  # 分页查询时每页的行数。
    totalPage: Any  # 总页数


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbIplistenerListReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbIplistenerListReturnObjResponse(None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbIplistenerListResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtelbIplistenerListReturnObjResponse]  # 接口业务数据


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbIplistenerListResponse':
        if not json_data:
            return None
        obj = CtelbIplistenerListResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 查看ip_listener列表
class CtelbIplistenerListApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbIplistenerListRequest) -> CtelbIplistenerListResponse:
        url = endpoint + "/v4/iplistener/list"
        params = {'regionID':request.regionID, 'ipListenerID':request.ipListenerID, 'pageNumber':request.pageNumber, 'pageSize':request.pageSize}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtelbIplistenerListResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
