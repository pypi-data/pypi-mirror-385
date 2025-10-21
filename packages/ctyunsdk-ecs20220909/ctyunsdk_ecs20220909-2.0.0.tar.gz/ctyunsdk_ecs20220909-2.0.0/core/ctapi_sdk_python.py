# encoding: utf-8
import urllib

import requests
import json
import hashlib
import base64
import hmac
import datetime
import uuid
import os
import sys

if sys.version_info.major == 2:
    from urllib import quote

    sys.setdefaultencoding('utf8')
else:
    from urllib.parse import quote
    from importlib import reload
import xml.etree.ElementTree as ET

reload(sys)

METHOD_GET = 'GET'
METHOD_POST = 'POST'
METHOD_HEAD = 'HEAD'
METHOD_PATCH = 'PATCH'
METHOD_PUT = 'PUT'
METHOD_DELETE = 'DELETE'
# file：参数中是否包含文件类型
file = False
ak = ""
sk = ""

def hmac_sha256(secret, data):
    if type(secret) == bytes:
        secret = bytearray(secret)
    else:
        secret = bytearray(secret, 'utf8')
    data = bytearray(data, 'utf8')
    return hmac.new(secret, data, digestmod=hashlib.sha256).digest()


def base64_of_hmac(data):
    return base64.b64encode(data)


def get_request_uuid():
    return str(uuid.uuid1())


def get_sorted_str(data, method):
    """
    鉴权用的参数整理
    :param data: dict 需要整理的参数
    :return: str
    """
    if isinstance(data, str):
        # data = eval(data)
        data = json.loads(data)
    sorted_data = sorted(data.items(), key=lambda item: item[0])
    str_list = map(lambda x_y: '%s=%s' % (x_y[0], x_y[1]), sorted_data)
    return '&'.join(str_list)


def build_sign(ak, sk, query_params, body_params, eop_date, request_uuid, method, file, content_type):
    """
    计算鉴权字段
    :param query_params: dict get请求中的参数
    :param body_params: dict post请求中的参数
    :param eop_date: str 请求时间，格式为：'%Y%m%dT%H%M%SZ'
    :return: str
    """
    body_str = ""
    if not file:
        body_str = json.dumps(body_params) if body_params else ''
    if method == "POST" or method == "PUT":
        if file:
            body_digest = hashlib.sha256(body_params).hexdigest()
        else:
            if isinstance(body_params, dict):
                body_digest = hashlib.sha256(json.dumps(body_params).encode('utf-8')).hexdigest()
            else:
                body_digest = hashlib.sha256(body_params.encode('utf-8')).hexdigest()
    else:
        body_digest = hashlib.sha256(body_str.encode('utf-8')).hexdigest()
    # 请求头中必要的两个参数
    header_str = 'ctyun-eop-request-id:%s\neop-date:%s\n' % (request_uuid, eop_date)
    # url中的参数，或get参数
    query_str = encodeQueryStr(get_sorted_str(query_params, method))
    signature_str = '%s\n%s\n%s' % (header_str, query_str, body_digest)
    print_log(repr('signature_str is: %s' % signature_str))
    sign_date = eop_date.split('T')[0]
    # 计算鉴权密钥
    k_time = hmac_sha256(sk, eop_date)
    k_ak = hmac_sha256(k_time, ak)
    k_date = hmac_sha256(k_ak, sign_date)

    signature_base64 = base64_of_hmac(hmac_sha256(k_date, signature_str))
    # 构建请求头的鉴权字段值
    sign_header = '%s Headers=ctyun-eop-request-id;eop-date Signature=%s' % (ak, signature_base64.decode('utf8'))
    return sign_header.encode('utf8')


def get_sign_headers(ak, sk, query_params, body, method, content_type, file, uuid):
    """
    获取鉴权用的请求头参数
    :param query_params: dict get请求中的参数
    :param body: dict post请求中的参数
    :return:
    """
    now = datetime.datetime.now()
    eop_date = datetime.datetime.strftime(now, '%Y%m%dT%H%M%SZ')
    headers = {  # 三个鉴权用的参数 User-Agent固定写法，确定该请求为pysdk发出
        'User-Agent': 'Mozilla/5.0(pysdk)',
        'Content-type': content_type,
        'ctyun-eop-request-id': uuid,
        'Eop-Authorization': build_sign(ak=ak, sk=sk, query_params=query_params, body_params=body, eop_date=eop_date,
                                        request_uuid=uuid, method=method, file=file, content_type=content_type),
        'Eop-date': eop_date,
    }
    return headers


def get(url, query="", params=None, header_params=None, content_type='application/json;charset=UTF-8'):
    queryParam = query
    querystr = ""
    if queryParam:
        for key, value in queryParam.items():
            querystr = str(querystr) + str(key) + "=" + str(value) + "&"
        if len(querystr) > 0:
            querystr = querystr[0: len(querystr) - 1]
    return execute(ak, sk, url, queryParam, querystr, method=METHOD_GET, params=params, header_params=header_params,
                   content_type=content_type)


def post(url, query="", params=None, header_params=None, content_type='application/json;charset=UTF-8'):
    queryParam = query
    querystr = ""
    if queryParam:
        for key, value in queryParam.items():
            querystr = str(querystr) + str(key) + "=" + str(value) + "&"
        if len(querystr) > 0:
            querystr = querystr[0: len(querystr) - 1]
    return execute(ak, sk, url, queryParam, querystr, method=METHOD_POST, params=params, header_params=header_params,
                   content_type=content_type)


# 一些新增的调用方法
def delete(url, query="", params=None, header_params=None, content_type='application/json;charset=UTF-8'):
    queryParam = query
    querystr = ""
    if queryParam:
        for key, value in queryParam.items():
            querystr = str(querystr) + str(key) + "=" + str(value) + "&"
        if len(querystr) > 0:
            querystr = querystr[0: len(querystr) - 1]
    return execute(ak, sk, url, queryParam, querystr, method=METHOD_DELETE, params=params, header_params=header_params,
                   content_type=content_type)


def put(url, query="", params=None, header_params=None, content_type='application/json;charset=UTF-8'):
    queryParam = query
    querystr = ""
    if queryParam:
        for key, value in queryParam.items():
            querystr = str(querystr) + str(key) + "=" + str(value) + "&"
        if len(querystr) > 0:
            querystr = querystr[0: len(querystr) - 1]
    return execute(ak, sk, url, queryParam, querystr, method=METHOD_PUT, params=params, header_params=header_params,
                   content_type=content_type)


def patch(url, query="", params=None, header_params=None, content_type='application/json;charset=UTF-8'):
    queryParam = query
    querystr = ""
    if queryParam:
        for key, value in queryParam.items():
            querystr = str(querystr) + str(key) + "=" + str(value) + "&"
        if len(querystr) > 0:
            querystr = querystr[0: len(querystr) - 1]
    return execute(ak, sk, url, queryParam, querystr, method=METHOD_PATCH, params=params, header_params=header_params,
                   content_type=content_type)


def head(url, query="", params=None, header_params=None, content_type='application/json;charset=UTF-8'):
    queryParam = query
    querystr = ""
    if queryParam:
        for key, value in queryParam.items():
            querystr = str(querystr) + str(key) + "=" + str(value) + "&"
        if len(querystr) > 0:
            querystr = querystr[0: len(querystr) - 1]
    return execute(ak, sk, url, queryParam, querystr, method=METHOD_HEAD, params=params, header_params=header_params,
                   content_type=content_type)


def execute(ak, sk, url, query, querystr, method, params=None, header_params=None,
            content_type='application/json;charset=UTF-8',
            file=bool(0), uuid=None):
    params = params or {}
    if 'application/x-www-form-urlencoded' in content_type:
        params = urllib.urlencode(params)
    header_params = header_params or {}
    # if method == "GET":
    #     query_params, body = (params, {})
    #     query = query_params
    # else:
    query_params = {}
    if len(querystr) > 0:
        for q in querystr.split('&'):
            query_params[q.split("=")[0]] = q.split("=")[1]
    body = params
    query = query_params
    request_uuid = get_request_uuid()
    headers = get_sign_headers(ak, sk, query, body, method, content_type, file, request_uuid)
    if not isinstance(header_params, dict):
        #eval
        headers.update(json.loads(header_params))
    else:
        headers.update(header_params)
#     headers.update(
#           {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/110.0"
#     #     #     ,"x-amz-acl": "private"  部分情况下x-amz-acl会参与加密，视情况加
#            }
# )
    if not len(querystr) == 0:
        url = url + "?" + encodeQueryStr(str(querystr))
    print_log('url: %s' % url)
    print_log('请求方式: %s' % method)
    print_log('请求头:\n %s' % headers)
    print_log('请求参数:\n %s' % params)
    print_log('请求参数类型:\n %s' % type(params))
    requests.packages.urllib3.disable_warnings()

    if method == METHOD_GET:
        res = requests.get(url, params=params, headers=headers, verify=False)
    elif method == METHOD_POST:
        if 'application/x-www-form-urlencoded' in content_type:
            res = requests.post(url, data=params, headers=headers, verify=False)
        elif 'multipart/form-data' in content_type:
            res = requests.post(url, data=params, headers=headers, verify=False)
        else:
            res = requests.post(url, json=params, headers=headers, verify=False)
    elif method == METHOD_PATCH:
        if 'application/x-www-form-urlencoded' in content_type:
            res = requests.patch(url, data=params, headers=headers, verify=False)
        elif 'multipart/form-data' in content_type:
            res = requests.patch(url, data=params, headers=headers, verify=False)
        else:
            res = requests.patch(url, json=params, headers=headers, verify=False)
    elif method == METHOD_HEAD:
       if 'application/x-www-form-urlencoded' in content_type:
           res = requests.head(url, data=params, headers=headers, verify=False)
       elif 'multipart/form-data' in content_type:
           res = requests.head(url, data=params, headers=headers, verify=False)
       else:
          res = requests.head(url, json=params, headers=headers, verify=False)
    elif method == METHOD_PUT:
        if 'application/x-www-form-urlencoded' in content_type:
           res = requests.put(url, data=params, headers=headers, verify=False)
        elif 'multipart/form-data' in content_type:
           res = requests.put(url, data=params, headers=headers, verify=False)
        else:
           res = requests.put(url, json=params, headers=headers, verify=False)
    elif method == METHOD_DELETE:
         if 'application/x-www-form-urlencoded' in content_type:
            res = requests.delete(url, data=params, headers=headers, verify=False)
         elif 'multipart/form-data' in content_type:
            res = requests.delete(url, data=params, headers=headers, verify=False)
         else:
            res = requests.delete(url, json=params, headers=headers, verify=False)

    print_log('返回状态码: %s' % res.status_code)
    # if(content_type =="application/xml"):
    print_log('返回: %s' % res.content.decode("utf-8"))
    # else:
    #    print_log('返回: %s' % res.text)
    # dict = dict(res.json())
    # ctresponse = CTResponse(res.status_code, res.text, None, res.headers, dict)
    # print(ctresponse)
    # return ctresponse
    return res.content.decode("utf-8")


def print_log(log_info):
    now = datetime.datetime.now()
    log_info = '[%s]: %s' % (str(now), log_info)
    print(log_info)


def encodeQueryStr(query):
    afterQuery = ""
    if (len(query) != 0):
        print(query)
        param = query.split("&")
        param.sort()
        for str in param:
            if (len(afterQuery) < 1):
                s = str.split("=")
                if (len(s) <= 2 and len(s) >= 2):
                    encodeStr = quote(s[1])
                    str = s[0] + "=" + encodeStr
                    afterQuery = afterQuery + str
                else:
                    encodeStr = ""
                    str = s[0] + "=" + encodeStr
                    afterQuery = afterQuery + str
            else:
                s = str.split("=")
                if (len(s) >= 2):
                    encodeStr = quote(s[1])
                    str = s[0] + "=" + encodeStr
                    afterQuery = afterQuery + "&" + str
                else:
                    encodeStr = ""
                    str = s[0] + "=" + encodeStr
                    afterQuery = afterQuery + "&" + str

    return afterQuery


def generate_body(file_list, boundary, params):
    lastbody = bytearray()
    for file in file_list:
        file_name_key = list(file.keys())[0]
        file_path = list(file.values())[0]
        file_name = os.path.basename(file_path)
        body1_array = bytearray(
            '--' + boundary + "\r\n" + "Content-Disposition: form-data; name=\"" + file_name_key + "\"; filename=\"" + file_name + "\r\n" + "Content-Type: application/octet-stream" + "\r\n" + "\r\n",
            'utf8')
        # body1_array = bytearray('--' + boundary + "\r\n" + "Content-Disposition: form-data; filename=\"" + filename + "\"\r\n" + "Content-Type: application/octet-stream" + "\r\n" + "\r\n")
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                body2_array = bytearray(f.read())
        body3_array = bytearray("\r\n", 'utf8')
        lastbody.extend(body1_array)
        lastbody.extend(body2_array)
        lastbody.extend(body3_array)

    if len(params) and params[0] != {}:
        for param in params:
            body1_array = bytearray(
                '--' + boundary + "\r\n" + "Content-Disposition: form-data; name=\"" + list(param.keys())[
                    0] + "\r\n" + "\r\n" + list(param.values())[0] + "\r\n", 'utf8')
            body3_array = bytearray("\r\n")
            lastbody.extend(body1_array)
            lastbody.extend(body3_array)
    body4_array = bytearray('--' + boundary + "--\r\n", 'utf8')
    lastbody.extend(body4_array)
    return lastbody


def convert_obj_to_xml(obj):
    root = ET.Element("__root__")
    convert_obj_to_xml_recursive(obj, root)
    child_elements = root.getchildren()

    xml_str = ""
    for element in child_elements:
        xml_str += ET.tostring(element, encoding='utf-8').decode('utf-8')

    return xml_str


def convert_obj_to_xml_recursive(obj, parent_element):
    for attr, value in obj.__dict__.items():
        if value is None or value == "":
            continue

        if isinstance(value, (str, int, float)):
            element = ET.SubElement(parent_element, attr)
            element.text = str(value)
        elif isinstance(value, list):
            for item in value:
                if hasattr(item, '__dict__'):
                    element = ET.SubElement(parent_element, attr)
                    convert_obj_to_xml_recursive(item, element)
                else:
                    element = ET.SubElement(parent_element, attr)
                    element.text = str(item)
        elif hasattr(value, '__dict__'):
            element = ET.SubElement(parent_element, attr)
            convert_obj_to_xml_recursive(value, element)