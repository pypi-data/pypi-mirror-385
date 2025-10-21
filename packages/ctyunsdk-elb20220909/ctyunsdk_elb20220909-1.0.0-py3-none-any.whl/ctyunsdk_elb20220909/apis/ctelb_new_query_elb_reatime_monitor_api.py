from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbNewQueryElbReatimeMonitorRequest:
    regionID: str  # 资源池 ID
    deviceIDs: Optional[List[Optional[str]]]  # 负载均衡 ID 列表
    pageNumber: Any  # 列表的页码，默认值为 1
    pageNo: Any  # 列表的页码，默认值为 1, 推荐使用该字段, pageNumber 后续会废弃
    pageSize: Any  # 每页数据量大小，取值 1-50


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbNewQueryElbReatimeMonitorRequest':
        if not json_data:
            return None
        obj = CtelbNewQueryElbReatimeMonitorRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbNewQueryElbReatimeMonitorReturnObjMonitorsResponse:
    lastUpdated: Optional[str]  # 最近更新时间
    regionID: Optional[str]  # 资源池 ID
    deviceID: Optional[str]  # 弹性公网 IP


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbNewQueryElbReatimeMonitorReturnObjMonitorsResponse':
        if not json_data:
            return None
        obj = CtelbNewQueryElbReatimeMonitorReturnObjMonitorsResponse(None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbNewQueryElbReatimeMonitorReturnObjResponse:
    """返回结果"""
    monitors: Optional[List[Optional[CtelbNewQueryElbReatimeMonitorReturnObjMonitorsResponse]]]  # 监控数据
    totalCount: Any  # 列表条目数
    currentCount: Any  # 分页查询时每页的行数。
    totalPage: Any  # 总页数


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbNewQueryElbReatimeMonitorReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbNewQueryElbReatimeMonitorReturnObjResponse(None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbNewQueryElbReatimeMonitorResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtelbNewQueryElbReatimeMonitorReturnObjResponse]  # 返回结果


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbNewQueryElbReatimeMonitorResponse':
        if not json_data:
            return None
        obj = CtelbNewQueryElbReatimeMonitorResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 查看负载均衡实时监控。
class CtelbNewQueryElbReatimeMonitorApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbNewQueryElbReatimeMonitorRequest) -> CtelbNewQueryElbReatimeMonitorResponse:
        url = endpoint + "/v4/elb/new-query-realtime-monitor"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtelbNewQueryElbReatimeMonitorResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
