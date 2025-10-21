import hmac
import base64
import hashlib
import datetime
import json
from .utils import get_sorted_str

class CtyunSigner:
    """天翼云签名器"""
    @staticmethod
    def sign(credential, params, body, method, content_type, request_id):
        """生成签名"""
        now = datetime.datetime.now()
        eop_date = now.strftime('%Y%m%dT%H%M%SZ')

        # 构建签名字符串
        header_str = f'ctyun-eop-request-id:{request_id}\neop-date:{eop_date}\n'
        query_str = get_sorted_str(params, method)
        body_digest = CtyunSigner._calculate_body_digest(body, method)
        
        signature_str = f'{header_str}\n{query_str}\n{body_digest}'

        sign_date = eop_date.split('T')[0]
        k_time = CtyunSigner._hmac_sha256(credential.sk, eop_date)
        k_ak = CtyunSigner._hmac_sha256(k_time, credential.ak)
        k_date = CtyunSigner._hmac_sha256(k_ak, sign_date)
        # 计算签名
        signature_base64 = base64.b64encode(CtyunSigner._hmac_sha256(k_date, signature_str))
        sign_header = '%s Headers=ctyun-eop-request-id;eop-date Signature=%s' % (credential.ak, signature_base64.decode('utf8'))

        return sign_header

    @staticmethod
    def _hmac_sha256(key, data):
        """HMAC-SHA256计算"""
        if isinstance(key, str):
            key = key.encode('utf-8')
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hmac.new(key, data, hashlib.sha256).digest()

    @staticmethod
    def _calculate_body_digest(body, method):
        """计算请求体摘要"""
        if not body:
            return hashlib.sha256(b'').hexdigest()
        if isinstance(body, dict):
            body = json.dumps(body)
        return hashlib.sha256(body.encode('utf-8')).hexdigest() 