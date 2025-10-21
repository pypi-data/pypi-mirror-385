import json

from typing import Optional, Dict, Any

import requests

from .exception import CtyunRequestException
from .signer import CtyunSigner
import uuid
import datetime

from .utils import extract_header_params, filter_header_params, get_sorted_params, params_to_query_string


class CtyunClient:
    """天翼云客户端"""
    
    def __init__(self):
        self.session = requests.Session()
        self.headers = {}
        # 禁用所有代理
        self.session.trust_env = False

    def post(self, url: str, header_params: set[str] = None, data: Optional[Dict] = None, credential=None, **kwargs) -> Any:
        """发送POST请求"""
        try:
            header_param = extract_header_params(header_params, data)
            # 将请求对象转换为字典
            request_data = self._convert_to_dict(data) if data else None
            
            # 生成请求ID
            request_id = str(uuid.uuid1())
            eop_date = datetime.datetime.now().strftime('%Y%m%dT%H%M%SZ')
            
            # 直接使用 CtyunSigner.sign
            signature = CtyunSigner.sign(
                credential=credential,
                params={},
                body=request_data,
                method='POST',
                content_type='application/json;charset=UTF-8',
                request_id=request_id
            )
            
            # 更新请求头
            headers = {
                'User-Agent': 'Mozilla/5.0(pysdk)',
                'Content-type': 'application/json;charset=UTF-8',
                'ctyun-eop-request-id': request_id,
                'Eop-Authorization': signature,
                'Eop-date': eop_date
            }

            self.headers = header_param
            self.headers.update(headers)
            
            # 打印请求信息
            print("Request URL:", url)
            print("Request Headers:", self.headers)
            print("Request Body:", request_data)
            
            # 检查端口是否为21443
            if ":21443" in url:
                kwargs['verify'] = False
            
            # 禁用代理
            kwargs['proxies'] = {'http': None, 'https': None}
                
            try:
                response = self.session.post(
                    url,
                    json=request_data,
                    headers=self.headers,
                    **kwargs
                )

                # 检查HTTP状态码是否小于200或大于等于300
                if response.status_code < 200 or response.status_code >= 300:
                    # 如果不是2xx成功状态码，修改响应内容，将statusCode设置为900
                    try:
                        response_data = response.json()
                        response_data['statusCode'] = 900
                        # 重新构建响应对象，保持原始状态码但修改内容
                        response._content = json.dumps(response_data).encode('utf-8')
                    except (json.JSONDecodeError, ValueError):
                        # 如果响应不是有效的JSON，创建一个新的错误响应
                        error_response = {
                            'statusCode': 900,
                            'message': f'HTTP请求失败，状态码: {response.status_code}',
                            'returnObj': None,
                            'requestId': request_id,
                            'code': 'HTTP_ERROR',
                            'error': response.text
                        }
                        response._content = json.dumps(error_response).encode('utf-8')

                response.raise_for_status()
            except Exception as e:
                # 捕获其他非预期的异常
                print(f"未知异常: {e}")
            
            # 打印响应信息
            print("Response Status:", response.status_code)
            print("Response Headers:", dict(response.headers))
            print("Response Body:", response.text)
            
            return response
        except Exception as e:
            raise CtyunRequestException(f"POST request failed: {str(e)}")

    def get(self, url: str, params: Optional[Dict] = None, header_params: Optional[Dict] = None, credential=None, **kwargs) -> Any:
        """发送GET请求"""
        try:
            paramss = {k: v for k, v in params.items() if v is not None}
            header_param = filter_header_params(header_params, params)

            # 生成请求ID
            request_id = str(uuid.uuid1())
            eop_date = datetime.datetime.now().strftime('%Y%m%dT%H%M%SZ')

            # 直接使用 CtyunSigner.sign
            signature = CtyunSigner.sign(
                credential=credential,
                params=paramss,
                body={},
                method='GET',
                content_type='application/json;charset=UTF-8',
                request_id=request_id
            )

            # 更新请求头
            headers = {
                'User-Agent': 'Mozilla/5.0(pysdk)',
                'Content-type': 'application/json;charset=UTF-8',
                'ctyun-eop-request-id': request_id,
                'Eop-Authorization': signature,
                'Eop-date': eop_date
            }
            self.headers = header_param
            self.headers.update(headers)

            # 打印请求信息
            print("Request URL:", url)
            print("Request Headers:", self.headers)
            # print("Request Body:", request_data)
            # 检查端口是否为21443，如果是则禁用SSL验证
            if ":21443" in url:
                kwargs['verify'] = False

            # 禁用代理
            kwargs['proxies'] = {'http': None, 'https': None}

            param = params_to_query_string(get_sorted_params(paramss))
            try:
                response = self.session.get(
                    url,
                    params=param,
                    headers=self.headers,
                    **kwargs
                )

                # 检查HTTP状态码是否小于200或大于等于300
                if response.status_code < 200 or response.status_code >= 300:
                    # 如果不是2xx成功状态码，修改响应内容，将statusCode设置为900
                    try:
                        response_data = response.json()
                        response_data['statusCode'] = 900
                        # 重新构建响应对象，保持原始状态码但修改内容
                        response._content = json.dumps(response_data).encode('utf-8')
                    except (json.JSONDecodeError, ValueError):
                        # 如果响应不是有效的JSON，创建一个新的错误响应
                        error_response = {
                            'statusCode': 900,
                            'message': f'HTTP请求失败，状态码: {response.status_code}',
                            'returnObj': None,
                            'requestId': request_id,
                            'code': 'HTTP_ERROR',
                            'error': response.text
                        }
                        response._content = json.dumps(error_response).encode('utf-8')

                response.raise_for_status()
            except Exception as e:
                # 捕获其他非预期的异常
                print(f"未知异常: {e}")

            # 打印响应信息
            print("Response Status:", response.status_code)
            print("Response Headers:", dict(response.headers))
            # print("Response Body:", response.text)

            return response
        except Exception as e:
            raise CtyunRequestException(f"GET request failed: {str(e)}")

    def _convert_to_dict(self, obj: Any) -> Dict:
        """将对象转换为可序列化的字典"""
        if hasattr(obj, '__dict__'):
            return {k: self._convert_to_dict(v) for k, v in obj.__dict__.items() if not k.startswith('_')}
        elif isinstance(obj, (list, tuple)):
            return [self._convert_to_dict(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: self._convert_to_dict(v) for k, v in obj.items()}
        else:
            return obj

    def put(self, url: str, data: Optional[Dict] = None, credential=None, **kwargs) -> Any:
        """发送PUT请求"""
        try:
            request_data = self._convert_to_dict(data) if data else None
            request_id = str(uuid.uuid1())
            eop_date = datetime.datetime.now().strftime('%Y%m%dT%H%M%SZ')
            
            signature = CtyunSigner.sign(
                credential=credential,
                params={},
                body=request_data,
                method='PUT',
                content_type='application/json;charset=UTF-8',
                request_id=request_id
            )
            
            headers = {
                'User-Agent': 'Mozilla/5.0(pysdk)',
                'Content-type': 'application/json;charset=UTF-8',
                'ctyun-eop-request-id': request_id,
                'Eop-Authorization': signature,
                'Eop-date': eop_date
            }
            self.headers.update(headers)
            
            if ":21443" in url:
                kwargs['verify'] = False
            kwargs['proxies'] = {'http': None, 'https': None}
                
            response = self.session.put(url, json=request_data, headers=self.headers, **kwargs)
            return response
        except Exception as e:
            raise CtyunRequestException(f"PUT request failed: {str(e)}")

    def delete(self, url: str, params: Optional[Dict] = None, credential=None, **kwargs) -> Any:
        """发送DELETE请求"""
        try:
            request_id = str(uuid.uuid1())
            eop_date = datetime.datetime.now().strftime('%Y%m%dT%H%M%SZ')
            
            signature = CtyunSigner.sign(
                credential=credential,
                params=params or {},
                body=None,
                method='DELETE',
                content_type='application/json;charset=UTF-8',
                request_id=request_id
            )
            
            headers = {
                'User-Agent': 'Mozilla/5.0(pysdk)',
                'Content-type': 'application/json;charset=UTF-8',
                'ctyun-eop-request-id': request_id,
                'Eop-Authorization': signature,
                'Eop-date': eop_date
            }
            self.headers.update(headers)
            
            if ":21443" in url:
                kwargs['verify'] = False
            kwargs['proxies'] = {'http': None, 'https': None}
                
            response = self.session.delete(url, params=params, headers=self.headers, **kwargs)
            return response
        except Exception as e:
            raise CtyunRequestException(f"DELETE request failed: {str(e)}")

    def patch(self, url: str, data: Optional[Dict] = None, credential=None, **kwargs) -> Any:
        """发送PATCH请求"""
        try:
            request_data = self._convert_to_dict(data) if data else None
            request_id = str(uuid.uuid1())
            eop_date = datetime.datetime.now().strftime('%Y%m%dT%H%M%SZ')
            
            signature = CtyunSigner.sign(
                credential=credential,
                params={},
                body=request_data,
                method='PATCH',
                content_type='application/json;charset=UTF-8',
                request_id=request_id
            )
            
            headers = {
                'User-Agent': 'Mozilla/5.0(pysdk)',
                'Content-type': 'application/json;charset=UTF-8',
                'ctyun-eop-request-id': request_id,
                'Eop-Authorization': signature,
                'Eop-date': eop_date
            }
            self.headers.update(headers)
            
            if ":21443" in url:
                kwargs['verify'] = False
            kwargs['proxies'] = {'http': None, 'https': None}
                
            response = self.session.patch(url, json=request_data, headers=self.headers, **kwargs)
            return response
        except Exception as e:
            raise CtyunRequestException(f"PATCH request failed: {str(e)}")