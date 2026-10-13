import json
import allure
import requests
import urllib3.exceptions

from common.readyaml import ReadYamlData
from common.recordlog import logs
import pytest

from conf import setting


class SendRequest:
    """发送接口请求，暂时只写了get和post"""

    def __init__(self, cookie=None):
        self.cookie = cookie
        self.read = ReadYamlData()
        self.session = requests.session()

    def send_request(self, **kwargs):
        cookie = {}
        try:
            result = None
            # 登录接口是用同一个session发起请求，登录响应头set-cookie会自动存入session内部的cookiejar
            # 后续接口yaml不需要手动在请求头获取cookie
            result = self.session.request(**kwargs)
            set_cookie = requests.utils.dict_from_cookiejar(result.cookies)
            if set_cookie:
                cookie['cookies'] = set_cookie
                self.read.write_yaml_data(cookie)
                logs.info("cookie: %s" % cookie)
            logs.info("接口返回信息：%s" % result.text if result.text else result)
        except requests.exceptions.ConnectionError:
            logs.error("ConnectionError--连接异常")
            pytest.fail("接口请求异常，可能是request的连接数过多或请求速度过快导致")
        except requests.exceptions.HTTPError:
            logs.error("HTTPError--http异常")
            pytest.fail("http请求异常！")
        except requests.exceptions.RequestException as e:
            logs.error(e)
            pytest.fail("请求异常，请检查系统或数据是否正常！")
        return result

    def run_main(self, api_name, url, case_name, headers, method, cookies=None, files=None, **kwargs):
        """
        接口请求
        :param api_name: 接口名
        :param url: 接口地址
        :param case_name: 测试用例
        :param headers:请求头
        :param method:请求方法
        :param cookies：默认为空
        :param files: 上传文件接口
        :param kwargs: 请求参数，根据yaml文件的参数类型
        :return:
        """

        try:
            # 收集报告日志信息
            logs.info('接口名称：%s' % api_name)
            logs.info('请求地址：%s' % url)
            logs.info('请求方式：%s' % method)
            logs.info('测试用例名称：%s' % case_name)
            logs.info('请求头：%s' % headers)
            logs.info('Cookie：%s' % cookies)
            # 接口请求参数字典kwargs转为字符串，req_params是字符串，kwargs是字典dict
            req_params = json.dumps(kwargs, ensure_ascii=False)
            if "data" in kwargs.keys():
                # 把接口接口请求参数附加到allure测试报告中，在线报告里可以直接查看请求入参，方便调试
                allure.attach(req_params, f'请求参数：{req_params}', allure.attachment_type.TEXT)
                logs.info("请求参数：%s" % kwargs)
            elif "json" in kwargs.keys():
                allure.attach(req_params, f'请求参数:{req_params}', allure.attachment_type.TEXT)
                logs.info("请求参数：%s" % kwargs)
            elif "params" in kwargs.keys():
                allure.attach(req_params, f'请求参数:{req_params}', allure.attachment_type.TEXT)
                logs.info("请求参数：%s" % kwargs)
        except Exception as e:
            logs.error(e)

        requests.packages.urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = self.send_request(method=method,
                                     url=url,
                                     headers=headers,
                                     cookies=cookies,
                                     files=files,
                                     timeout=setting.API_TIMEOUT,
                                     verify=False,
                                     **kwargs)
        return response


if __name__ == '__main__':
    method = 'get'
    url = 'http://127.0.0.1:8787/coupApply/cms/goodsList'
    params = {
        "msgType": "getHandsetListOfCust",
        "page": 1,
        "size": 20
    }
    header = {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}

    send = SendRequest()
    res = send.run_main(name="商品列表接口",
                        case_name="查询商品列表调试用例",
                        method=method,
                        url=url,
                        params=params,
                        header=header)
    print(res)
