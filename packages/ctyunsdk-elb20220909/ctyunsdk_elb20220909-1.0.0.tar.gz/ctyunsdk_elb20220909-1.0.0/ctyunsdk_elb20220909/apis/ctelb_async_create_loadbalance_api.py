from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbAsyncCreateLoadbalanceRequest:
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 区域ID
    vpcID: Optional[str]  # vpc的ID
    subnetID: str  # 子网的ID
    name: str  # 唯一。支持拉丁字母、中文、数字，下划线，连字符，中文 / 英文字母开头，不能以 http: / https: 开头，长度 2 - 32
    description: Optional[str]  # 支持拉丁字母、中文、数字, 特殊字符：~!@#$%^&*()_-+= <>?:'{},./;'[,]·！@#￥%……&*（） —— -+={},《》？：“”【】、；‘'，。、，不能以 http: / https: 开头，长度 0 - 128
    eipID: Optional[str]  # 弹性公网IP的ID。当resourceType=external为必填
    resourceType: str  # 资源类型。internal：内网负载均衡，external：公网负载均衡
    privateIpAddress: Optional[str]  # 负载均衡的私有IP地址，不指定则自动分配


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbAsyncCreateLoadbalanceRequest':
        if not json_data:
            return None
        obj = CtelbAsyncCreateLoadbalanceRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbAsyncCreateLoadbalanceReturnObjResponse:
    """返回结果"""
    status: Optional[str]  # 创建进度: in_progress / done
    message: Optional[str]  # 进度说明
    loadBalanceID: Optional[str]  # 负载均衡ID，可能为 null


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbAsyncCreateLoadbalanceReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbAsyncCreateLoadbalanceReturnObjResponse(None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbAsyncCreateLoadbalanceResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtelbAsyncCreateLoadbalanceReturnObjResponse]  # 返回结果


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbAsyncCreateLoadbalanceResponse':
        if not json_data:
            return None
        obj = CtelbAsyncCreateLoadbalanceResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 创建负载均衡实例，该接口为异步接口，第一次请求会返回资源在创建中，需要用户发起多次请求，直到 status 为 done 为止。
class CtelbAsyncCreateLoadbalanceApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbAsyncCreateLoadbalanceRequest) -> CtelbAsyncCreateLoadbalanceResponse:
        url = endpoint + "/v4/elb/async-create-loadbalance"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtelbAsyncCreateLoadbalanceResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
