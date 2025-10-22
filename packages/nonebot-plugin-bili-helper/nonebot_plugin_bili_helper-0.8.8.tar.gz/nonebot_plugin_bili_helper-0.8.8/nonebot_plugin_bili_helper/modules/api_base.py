from typing import Tuple
import requests
import urllib.parse

class ApiEnv:
    'API 请求环境参数'

    def __init__(self, ua: str, refer: str):
        self.ua = ua
        self.refer = refer

    def get_encoder(self) -> 'ApiEncoder':
        '获取请求参数编码器，默认不进行编码'
        return None

    def check_result(self, result: dict) -> Tuple[bool, str]:
        '检查返回结果是否成功，以及对应的错误信息'
        return False, str(result)

class ApiEncoder:
    'API 请求参数编码器'

    def encode(self, url: str, params: dict) -> Tuple[str, dict]:
        '对请求参数进行编码，返回新的 url 和参数字典'
        return url, params

class ApiInfo:
    'API 请求接口信息'

    def __init__(self,
                 url: str,
                 params: dict,
                 errors: dict,
                 encoder: ApiEncoder=None,
                 ):
        self.url = url
        self.params = params
        self.errors = errors
        self.encoder = encoder

class ApiInvoker:
    'API 请求调用器'

    def __init__(self, env: ApiEnv, api_info: ApiInfo):
        self.env = env
        self.api_info = api_info

    def call(self, headers: dict = {}):
        ua = self.env.ua
        refer = self.env.refer
        cookie = self.env.cookie
        api_info = self.api_info

        url = api_info.url
        params = api_info.params
        errors = api_info.errors
        encoder = api_info.encoder
        headers = {
            'User-Agent': ua,
            'Referer': refer,
            'Cookie': cookie,
            **headers
        }
        final_params = params

        if encoder:
            url, final_params = encoder.encode(url, final_params)

        query = urllib.parse.urlencode(final_params)
        full_url = f'{url}?{query}'
        # print('Request URL:', full_url)
        # print('Request Headers:', headers)
        resp = requests.get(full_url, headers=headers)
        resp.raise_for_status()
        json_content = resp.json()
        # print('Response JSON:', json_content)
        [res_code, res_msg] = self.env.check_result(json_content)
        error_msg = errors.get(str(res_code), res_msg or '未知错误')
        if res_code != 0 and res_msg != '成功':
            raise Exception(f'API 请求失败，错误代码 {res_code}：{error_msg}')
        return json_content
