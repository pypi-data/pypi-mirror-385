from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbListDomainCertLinksRequest:
    regionID: str  # 资源池ID
    listenerID: Optional[str]  # 监听器 ID


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbListDomainCertLinksRequest':
        if not json_data:
            return None
        obj = CtelbListDomainCertLinksRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbListDomainCertLinksReturnObjResponse:
    certificateName: Optional[str]  # 多证书 id
    certificateType: Optional[str]  # 类型类型: ca / certificate
    extDomainName: Optional[str]  # 扩展域名
    createdTime: Optional[str]  # 创建时间
    domainCertID: Optional[str]  # 多证书 id


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbListDomainCertLinksReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbListDomainCertLinksReturnObjResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbListDomainCertLinksResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[List[Optional[CtelbListDomainCertLinksReturnObjResponse]]]  # 检查结果


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbListDomainCertLinksResponse':
        if not json_data:
            return None
        obj = CtelbListDomainCertLinksResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 获取多证书
class CtelbListDomainCertLinksApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbListDomainCertLinksRequest) -> CtelbListDomainCertLinksResponse:
        url = endpoint + "/v4/elb/list-domain-cert-links"
        params = {'regionID':request.regionID, 'listenerID':request.listenerID}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtelbListDomainCertLinksResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
