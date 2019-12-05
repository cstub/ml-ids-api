from typing import List
import datetime
import hashlib
import hmac
import urllib.parse
import requests
from requests.exceptions import RequestException


class AwsSagemakerHttpClientError(IOError):

    def __init__(self, cause, status_code=None, response_body=None):
        self.cause = cause
        self.status_code = status_code
        self.response_body = response_body
        super(IOError, self).__init__()

    def __str__(self):
        return 'AwsSagemakerHttpClientError: [{}]. Status Code: [{}]. Response Body: [{}].' \
            .format(self.cause, self.status_code, self.response_body)


class AwsSagemakerHttpClient(object):

    def __init__(self, access_key, secret_key, schema, host, endpoint, region):
        self.access_key = access_key
        self.secret_key = secret_key
        self.schema = schema
        self.host = host
        self.endpoint = endpoint
        self.region = region
        self.service = 'sagemaker'
        self.algorithm = 'AWS4-HMAC-SHA256'
        self.url = urllib.parse.urljoin(schema + '://' + host, endpoint)

    def post_invocations(self, request_body: str) -> List[int]:
        content_type = 'application/json; format=pandas-split'
        now = datetime.datetime.utcnow()
        amz_date = now.strftime('%Y%m%dT%H%M%SZ')

        authorization_header = self._create_authorization_header(method='POST',
                                                                 time=now,
                                                                 amz_date=amz_date,
                                                                 content_type=content_type,
                                                                 request_body=request_body)

        headers = {'Content-Type': content_type,
                   'X-Amz-Date': amz_date,
                   'Authorization': authorization_header}

        response = None

        try:
            response = requests.post(url=self.url,
                                     data=request_body,
                                     headers=headers)

            response.raise_for_status()
            return response.json()
        except RequestException as http_err:
            body = response.text if response is not None else None
            status = response.status_code if response is not None else None
            raise AwsSagemakerHttpClientError(cause=http_err, status_code=status, response_body=body)

    def _create_authorization_header(self, method, time, amz_date, content_type, request_body):
        signed_headers = 'content-type;host;x-amz-date'
        date_stamp = time.strftime('%Y%m%d')
        credential_scope = date_stamp + '/' + self.region + '/' + self.service + '/' + 'aws4_request'

        canonical_request = self._create_canonical_request(method=method,
                                                           content_type=content_type,
                                                           amz_date=amz_date,
                                                           request_body=request_body,
                                                           signed_headers=signed_headers)

        string_to_sign = self._create_string_to_sign(amz_date=amz_date,
                                                     canonical_request=canonical_request,
                                                     credential_scope=credential_scope)

        signing_key = self._get_signature_key(self.secret_key, date_stamp, self.region, self.service)

        signature = self._create_signature(signing_key, string_to_sign)

        return self.algorithm + ' ' + 'Credential=' + self.access_key + '/' + credential_scope + ', ' \
               + 'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature

    def _create_canonical_request(self, method, content_type, amz_date, request_body, signed_headers, query_string=''):
        canonical_headers = 'content-type:' + content_type + '\n' + 'host:' + self.host + '\n' \
                            + 'x-amz-date:' + amz_date + '\n'
        payload_hash = hashlib.sha256(request_body).hexdigest()
        return method + '\n' + self.endpoint + '\n' + query_string + '\n' + canonical_headers + '\n' \
               + signed_headers + '\n' + payload_hash

    def _create_string_to_sign(self, amz_date, canonical_request, credential_scope):
        encoded_request = hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
        return self.algorithm + '\n' + amz_date + '\n' + credential_scope + '\n' + encoded_request

    def _get_signature_key(self, key, date_stamp, region_name, service_name):
        k_date = self._sign(('AWS4' + key).encode('utf-8'), date_stamp)
        k_region = self._sign(k_date, region_name)
        k_service = self._sign(k_region, service_name)
        k_signing = self._sign(k_service, 'aws4_request')
        return k_signing

    @staticmethod
    def _create_signature(signing_key, string_to_sign):
        return hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

    @staticmethod
    def _sign(key, msg):
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()
