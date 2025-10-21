from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbCreateDomainCertLinkRequest:
    regionID: str  # 资源池ID
    domainName: str  # 整个域名的总长度不能超过 255 个字符，每个子域名（包括顶级域名）的长度不能超过 63 个字符，域名中的字符集包括大写字母、小写字母、数字和连字符（减号），连字符不能位于域名的开头
    certificateID: str  # 证书 ID
    listenerID: str  # 监听器 ID
    description: Optional[str]  # 支持拉丁字母、中文、数字, 特殊字符：~!@#$%^&*()_-+= <>?:{},./;'[]·！@#￥%……&*（） —— -+={}\《》？：“”【】、；‘'，。、，不能以 http: / https: 开头，长度 0 - 128


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbCreateDomainCertLinkRequest':
        if not json_data:
            return None
        obj = CtelbCreateDomainCertLinkRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbCreateDomainCertLinkReturnObjResponse:
    """检查结果"""
    domainCertID: Optional[str]  # 多证书 id


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbCreateDomainCertLinkReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbCreateDomainCertLinkReturnObjResponse(None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbCreateDomainCertLinkResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtelbCreateDomainCertLinkReturnObjResponse]  # 检查结果


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbCreateDomainCertLinkResponse':
        if not json_data:
            return None
        obj = CtelbCreateDomainCertLinkResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 创建多证书
class CtelbCreateDomainCertLinkApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbCreateDomainCertLinkRequest) -> CtelbCreateDomainCertLinkResponse:
        url = endpoint + "/v4/elb/create-domain-cert-links"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtelbCreateDomainCertLinkResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
