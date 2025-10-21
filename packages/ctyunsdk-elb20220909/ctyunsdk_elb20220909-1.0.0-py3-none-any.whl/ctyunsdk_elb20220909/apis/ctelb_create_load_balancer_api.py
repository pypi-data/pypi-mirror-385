from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbCreateLoadBalancerRequest:
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 区域ID
    projectID: Optional[str]  # 企业项目 ID，默认为'0'
    vpcID: Optional[str]  # vpc的ID
    subnetID: str  # 子网的ID
    name: str  # 唯一。支持拉丁字母、中文、数字，下划线，连字符，中文 / 英文字母开头，不能以 http: / https: 开头，长度 2 - 32
    description: Optional[str]  # 支持拉丁字母、中文、数字, 特殊字符：~!@#$%^&*()_-+= <>?:{},./;'[]·！@#￥%……&*（） —— -+={}\|《》？：“”【】、；‘'，。、，不能以 http: / https: 开头，长度 0 - 128
    eipID: Optional[str]  # 弹性公网IP的ID。当resourceType=external为必填
    slaName: str  # lb的规格名称,支持elb.s1.small和elb.default，默认为elb.default，均为经典型负载均衡
    resourceType: str  # 资源类型。internal：内网负载均衡，external：公网负载均衡
    privateIpAddress: Optional[str]  # 负载均衡的私有IP地址，不指定则自动分配
    deleteProtection: Optional[bool]  # 删除保护。false（不开启）、true（开）。 默认：不开启


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbCreateLoadBalancerRequest':
        if not json_data:
            return None
        obj = CtelbCreateLoadBalancerRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbCreateLoadBalancerReturnObjResponse:
    """返回结果"""
    iD: Optional[str]  # 负载均衡ID


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbCreateLoadBalancerReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbCreateLoadBalancerReturnObjResponse(None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbCreateLoadBalancerResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtelbCreateLoadBalancerReturnObjResponse]  # 返回结果


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbCreateLoadBalancerResponse':
        if not json_data:
            return None
        obj = CtelbCreateLoadBalancerResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 创建负载均衡实例
class CtelbCreateLoadBalancerApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbCreateLoadBalancerRequest) -> CtelbCreateLoadBalancerResponse:
        url = endpoint + "/v4/elb/create-loadbalancer"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtelbCreateLoadBalancerResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
