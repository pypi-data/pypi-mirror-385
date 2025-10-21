from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbCreatePgelbRequest:
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 区域ID
    projectID: Optional[str]  # 企业项目 ID，默认为'0'
    vpcID: Optional[str]  # vpc的ID
    subnetID: str  # 子网的ID
    name: str  # 唯一。支持拉丁字母、中文、数字，下划线，连字符，中文 / 英文字母开头，不能以 http: / https: 开头，长度 2 - 32
    description: Optional[str]  # 支持拉丁字母、中文、数字, 特殊字符：~!@#$%^&*()_-+= <>?:'{},./;'[]·！@#￥%……&*（） —— -+={},《》？：“”【】、；‘'，。、，不能以 http: / https: 开头，长度 0 - 128
    eipID: Optional[str]  # 弹性公网IP的ID。当resourceType=external为必填
    slaName: str  # lb的规格名称, 支持:elb.s2.small，elb.s3.small，elb.s4.small，elb.s5.small，elb.s2.large，elb.s3.large，elb.s4.large，elb.s5.large——"elb.s2.small": "standardI"（标准型Ⅰ）, "elb.s2.large": "standardII"（标准型Ⅱ）、"elb.s3.small": "enhancedI"（增强型Ⅰ）, "elb.s3.large": "enhancedII"（增强型Ⅱ）、"elb.s4.small": "higherI"（高阶型Ⅰ）, "elb.s4.large": "higherII"（高阶型Ⅱ）、"elb.s5.small": "superI"（超强型Ⅰ）, "elb.s5.large": "superII"（超强型Ⅱ）
    resourceType: str  # 资源类型。internal：内网负载均衡，external：公网负载均衡
    privateIpAddress: Optional[str]  # 负载均衡的私有IP地址，不指定则自动分配
    cycleType: str  # 订购类型：month（包月） / year（包年） / on_demand （按需)
    cycleCount: Any  # 订购时长, 当 cycleType = month, 支持续订 1 - 11 个月; 当 cycleType = year, 支持续订 1 - 3 年，当 cycleType = on_demand 可以不传
    payVoucherPrice: Optional[str]  # 代金券金额，支持到小数点后两位


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbCreatePgelbRequest':
        if not json_data:
            return None
        obj = CtelbCreatePgelbRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbCreatePgelbReturnObjResponse:
    """业务数据"""
    masterOrderID: Optional[str]  # 订单id。
    masterOrderNO: Optional[str]  # 订单编号, 可以为 null。
    masterResourceStatus: Optional[str]  # 资源状态: started（启用） / renewed（续订） / refunded（退订） / destroyed（销毁） / failed（失败） / starting（正在启用） / changed（变配）/ expired（过期）/ unknown（未知）
    masterResourceID: Optional[str]  # 资源 ID 可以为 null。
    regionID: Optional[str]  # 可用区id。
    elbID: Optional[str]  # 负载均衡 ID


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbCreatePgelbReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbCreatePgelbReturnObjResponse(None,None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbCreatePgelbResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtelbCreatePgelbReturnObjResponse]  # 业务数据


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbCreatePgelbResponse':
        if not json_data:
            return None
        obj = CtelbCreatePgelbResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 保障型负载均衡创建
class CtelbCreatePgelbApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbCreatePgelbRequest) -> CtelbCreatePgelbResponse:
        url = endpoint + "/v4/elb/create-pgelb"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtelbCreatePgelbResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
