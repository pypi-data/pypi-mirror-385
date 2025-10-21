from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbQueryCreatePgelbPriceRequest:
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 区域ID
    projectID: Optional[str]  # 企业项目 ID，默认为'0'
    vpcID: Optional[str]  # vpc的ID
    subnetID: str  # 子网的ID
    name: str  # 支持拉丁字母、中文、数字，下划线，连字符，中文 / 英文字母开头，不能以 http: / https: 开头，长度 2 - 32
    description: Optional[str]  # 支持拉丁字母、中文、数字, 特殊字符：~!@#$%^&*()_-+= <>?:'{},./;'[]·！@#￥%……&*（） —— -+={},《》？：“”【】、；‘'，。、，不能以 http: / https: 开头，长度 0 - 128
    eipID: Optional[str]  # 弹性公网IP的ID。当resourceType=external为必填
    slaName: str  # lb的规格名称, 支持:elb.s2.small，elb.s3.small，elb.s4.small，elb.s5.small，elb.s2.large，elb.s3.large，elb.s4.large，elb.s5.large
    resourceType: str  # 资源类型。internal：内网负载均衡，external：公网负载均衡
    privateIpAddress: Optional[str]  # 负载均衡的私有IP地址，不指定则自动分配
    cycleType: str  # 订购类型：month（包月） / year（包年）
    cycleCount: Any  # 订购时长, 当 cycleType = month, 支持续订 1 - 11 个月; 当 cycleType = year, 支持续订 1 - 3 年


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbQueryCreatePgelbPriceRequest':
        if not json_data:
            return None
        obj = CtelbQueryCreatePgelbPriceRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbQueryCreatePgelbPriceReturnObjSubOrderPricesOrderItemPricesResponse:
    resourceType: Optional[str]  # 资源类型
    totalPrice: Optional[str]  # 总价格（单位：元）
    finalPrice: Optional[str]  # 最终价格（单位：元）


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbQueryCreatePgelbPriceReturnObjSubOrderPricesOrderItemPricesResponse':
        if not json_data:
            return None
        obj = CtelbQueryCreatePgelbPriceReturnObjSubOrderPricesOrderItemPricesResponse(None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbQueryCreatePgelbPriceReturnObjSubOrderPricesResponse:
    serviceTag: Optional[str]  # 服务类型
    totalPrice: Any  # 子订单总价格（单位：元）
    finalPrice: Any  # 最终价格（单位：元）
    orderItemPrices: Optional[List[Optional[CtelbQueryCreatePgelbPriceReturnObjSubOrderPricesOrderItemPricesResponse]]]  # item价格信息


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbQueryCreatePgelbPriceReturnObjSubOrderPricesResponse':
        if not json_data:
            return None
        obj = CtelbQueryCreatePgelbPriceReturnObjSubOrderPricesResponse(None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbQueryCreatePgelbPriceReturnObjResponse:
    """业务数据"""
    totalPrice: Any  # 总价格（单位：元）
    discountPrice: Any  # 折后价格（单位：元）
    finalPrice: Any  # 最终价格（单位：元）
    subOrderPrices: Optional[List[Optional[CtelbQueryCreatePgelbPriceReturnObjSubOrderPricesResponse]]]  # 子订单价格信息


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbQueryCreatePgelbPriceReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbQueryCreatePgelbPriceReturnObjResponse(None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbQueryCreatePgelbPriceResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtelbQueryCreatePgelbPriceReturnObjResponse]  # 业务数据


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbQueryCreatePgelbPriceResponse':
        if not json_data:
            return None
        obj = CtelbQueryCreatePgelbPriceResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 保障型负载均衡创建询价
class CtelbQueryCreatePgelbPriceApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbQueryCreatePgelbPriceRequest) -> CtelbQueryCreatePgelbPriceResponse:
        url = endpoint + "/v4/elb/query-create-price"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtelbQueryCreatePgelbPriceResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
