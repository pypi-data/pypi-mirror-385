from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbShowHealthCheckRequest:
    regionID: str  # 区域ID
    id: Optional[str]  # 健康检查ID, 后续废弃该字段
    healthCheckID: str  # 健康检查ID, 推荐使用该字段, 当同时使用 id 和 healthCheckID 时，优先使用 healthCheckID


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbShowHealthCheckRequest':
        if not json_data:
            return None
        obj = CtelbShowHealthCheckRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbShowHealthCheckReturnObjResponse:
    """接口业务数据"""
    regionID: Optional[str]  # 区域ID
    azName: Optional[str]  # 可用区名称
    projectID: Optional[str]  # 项目ID
    iD: Optional[str]  # 健康检查ID
    name: Optional[str]  # 健康检查名称
    description: Optional[str]  # 描述
    protocol: Optional[str]  # 健康检查协议: TCP / UDP / HTTP
    protocolPort: Any  # 健康检查端口
    timeout: Any  # 健康检查响应的最大超时时间
    integererval: Any  # 负载均衡进行健康检查的时间间隔
    maxRetry: Any  # 最大重试次数
    httpMethod: Optional[str]  # HTTP请求的方法
    httpUrlPath: Optional[str]  # HTTP请求url路径
    httpExpectedCodes: Optional[str]  # HTTP预期码
    status: Any  # 状态 1 表示 UP, 0 表示 DOWN
    createTime: Optional[str]  # 创建时间，为UTC格式


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbShowHealthCheckReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbShowHealthCheckReturnObjResponse(None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbShowHealthCheckResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtelbShowHealthCheckReturnObjResponse]  # 接口业务数据


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbShowHealthCheckResponse':
        if not json_data:
            return None
        obj = CtelbShowHealthCheckResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 查看健康检查详情
class CtelbShowHealthCheckApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbShowHealthCheckRequest) -> CtelbShowHealthCheckResponse:
        url = endpoint + "/v4/elb/show-health-check"
        params = {'regionID':request.regionID, 'id':request.id, 'healthCheckID':request.healthCheckID}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtelbShowHealthCheckResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
