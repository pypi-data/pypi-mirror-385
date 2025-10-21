from typing import List, Optional, Dict, Any
from ctyunsdk_bandwidth20220909.core.client import CtyunClient
from ctyunsdk_bandwidth20220909.core.credential import Credential
from ctyunsdk_bandwidth20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from dataclasses_json import dataclass_json

from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcCreateBandwidthRequest:
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 创建共享带宽的区域id。
    bandwidth: Any  # 共享带宽的带宽峰值，必须大于等于 5。5-1000
    cycleType: str  # 订购类型：包年/包月订购，或按需订购。<br>month / year / on_demand
    name: str  # 支持拉丁字母、中文、数字，下划线，连字符，中文 / 英文字母开头，不能以 http: / https: 开头，长度 2 - 32
    cycleCount: Optional[Any] = None # 订购时长, cycleType 是 on_demand 为可选，当 cycleType = month, 支持续订 1 - 11 个月; 当 cycleType = year, 支持续订 1 - 3 年
    payVoucherPrice: Optional[str] = None  # 代金券金额，支持到小数点后两位
    projectID: Optional[str] = None  # 企业项目 ID，默认为'0'


@dataclass_json
@dataclass
class CtvpcCreateBandwidthReturnObjResponse:
    """业务数据"""
    masterOrderID: Optional[str] = None  # 订单id。
    masterOrderNO: Optional[str] = None  # 订单编号, 可以为 null。
    masterResourceStatus: Optional[
        str] = None  # 资源状态: started（启用） / renewed（续订） / refunded（退订） / destroyed（销毁） / failed（失败） / starting（正在启用） / changed（变配）/ expired（过期）/ unknown（未知）
    masterResourceID: Optional[str] = None  # 可以为 null。
    regionID: Optional[str] = None  # 可用区id。
    bandwidthID: Optional[str] = None  # 带宽 ID，当 masterResourceStatus 不为 started, 该值可为 null


@dataclass_json
@dataclass
class CtvpcCreateBandwidthResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str] = None  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str] = None  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str] = None  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtvpcCreateBandwidthReturnObjResponse] = None  # 业务数据



# 调用此接口可创建共享带宽。
class CtvpcCreateBandwidthApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)

    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint

    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str,
           request: CtvpcCreateBandwidthRequest) -> CtvpcCreateBandwidthResponse:
        url = endpoint + "/v4/bandwidth/create"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict,
                                   credential=credential)
            return CtvpcCreateBandwidthResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
