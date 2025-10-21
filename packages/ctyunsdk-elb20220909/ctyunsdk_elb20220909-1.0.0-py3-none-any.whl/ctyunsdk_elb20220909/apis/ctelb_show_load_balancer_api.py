from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbShowLoadBalancerRequest:
    regionID: str  # 区域ID
    iD: Optional[str]  # 负载均衡ID, 该字段后续废弃
    elbID: str  # 负载均衡ID, 推荐使用该字段


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbShowLoadBalancerRequest':
        if not json_data:
            return None
        obj = CtelbShowLoadBalancerRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbShowLoadBalancerReturnObjEipInfoResponse:
    resourceID: Optional[str]  # 计费类资源ID
    eipID: Optional[str]  # 弹性公网IP的ID
    bandwidth: Any  # 弹性公网IP的带宽
    isTalkOrder: Optional[bool]  # 是否按需资源


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbShowLoadBalancerReturnObjEipInfoResponse':
        if not json_data:
            return None
        obj = CtelbShowLoadBalancerReturnObjEipInfoResponse(None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbShowLoadBalancerReturnObjResponse:
    regionID: Optional[str]  # 区域ID
    azName: Optional[str]  # 可用区名称
    iD: Optional[str]  # 负载均衡ID
    projectID: Optional[str]  # 项目ID
    name: Optional[str]  # 名称
    description: Optional[str]  # 描述
    vpcID: Optional[str]  # VPC ID
    subnetID: Optional[str]  # 子网ID
    portID: Optional[str]  # 负载均衡实例默认创建port ID
    privateIpAddress: Optional[str]  # 负载均衡实例的内网VIP
    ipv6Address: Optional[str]  # 负载均衡实例的IPv6地址
    slaName: Optional[str]  # 规格名称
    eipInfo: Optional[List[Optional[CtelbShowLoadBalancerReturnObjEipInfoResponse]]]  # 弹性公网IP信息
    deleteProtection: Optional[bool]  # 删除保护。开启，不开启
    adminStatus: Optional[str]  # 管理状态: DOWN / ACTIVE
    status: Optional[str]  # 负载均衡状态: DOWN / ACTIVE
    resourceType: Optional[str]  # 负载均衡类型: external / internal
    createdTime: Optional[str]  # 创建时间，为UTC格式
    updatedTime: Optional[str]  # 更新时间，为UTC格式


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbShowLoadBalancerReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbShowLoadBalancerReturnObjResponse(None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbShowLoadBalancerResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[List[Optional[CtelbShowLoadBalancerReturnObjResponse]]]  # 接口业务数据


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbShowLoadBalancerResponse':
        if not json_data:
            return None
        obj = CtelbShowLoadBalancerResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 查看负载均衡实例
class CtelbShowLoadBalancerApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbShowLoadBalancerRequest) -> CtelbShowLoadBalancerResponse:
        url = endpoint + "/v4/elb/show-loadbalancer"
        params = {'regionID':request.regionID, 'iD':request.iD, 'elbID':request.elbID}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtelbShowLoadBalancerResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
