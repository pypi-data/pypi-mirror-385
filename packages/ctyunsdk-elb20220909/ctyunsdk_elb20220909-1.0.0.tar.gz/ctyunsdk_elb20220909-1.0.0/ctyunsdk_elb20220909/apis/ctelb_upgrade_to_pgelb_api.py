from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbUpgradeToPgelbRequest:
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 区域ID
    elbID: str  # 负载均衡 ID
    slaName: str  # lb的规格名称, 支持:elb.s2.small，elb.s3.small，elb.s4.small，elb.s5.small，elb.s2.large，elb.s3.large，elb.s4.large，elb.s5.large
    cycleType: str  # 订购类型：month（包月） / year（包年）
    cycleCount: Any  # 订购时长, 当 cycleType = month, 支持续订 1 - 11 个月; 当 cycleType = year, 支持续订 1 - 3 年


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbUpgradeToPgelbRequest':
        if not json_data:
            return None
        obj = CtelbUpgradeToPgelbRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbUpgradeToPgelbReturnObjResponse:
    """业务数据"""
    masterOrderID: Optional[str]  # 订单id。
    masterOrderNO: Optional[str]  # 订单编号, 可以为 null。
    masterResourceStatus: Optional[str]  # 资源状态: started（启用） / renewed（续订） / refunded（退订） / destroyed（销毁） / failed（失败） / starting（正在启用） / changed（变配）/ expired（过期）/ unknown（未知）
    masterResourceID: Optional[str]  # 资源 ID 可以为 null。
    regionID: Optional[str]  # 可用区id。


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbUpgradeToPgelbReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbUpgradeToPgelbReturnObjResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbUpgradeToPgelbResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtelbUpgradeToPgelbReturnObjResponse]  # 业务数据


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbUpgradeToPgelbResponse':
        if not json_data:
            return None
        obj = CtelbUpgradeToPgelbResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 升级为保障型负载均衡
class CtelbUpgradeToPgelbApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbUpgradeToPgelbRequest) -> CtelbUpgradeToPgelbResponse:
        url = endpoint + "/v4/elb/upgrade-to-pgelb"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtelbUpgradeToPgelbResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
