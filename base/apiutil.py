import ast
import json
import re

import jsonpath
import pytest
import allure

from common.debugtalk import DebugTalk
from common.readyaml import get_testcase_yaml, ReadYamlData
from common.recordlog import logs
from common.sendrequest import SendRequest
from conf.operationConfig import OperationConfig
from common.assertions import Assertions


class RequestBase:

    def __init__(self):
        self.read = ReadYamlData()
        self.conf = OperationConfig()
        self.send = SendRequest()

    def replace_load(self, data):
        """
            yaml表达式解析替换工具，数据替换解析(为了实现在yaml文件中能调用python的方法)
            提取数据：${get_extract_data(token)}，${方法名(参数)}
        """
        print(data)
        str_data = data
        # isinstance(data,str)判断data是不是字符串
        if not isinstance(data, str):
            # 不是字符串则转成完整字符串，保留中文不转Unicode编码
            # 转为json格式的字符串
            str_data = json.dumps(data, ensure_ascii=False)
        # 循环处理所有${}占位符
        for i in range(str_data.count('${')):  # str_data.count('${')统计字符串有多少个${占位符
            print(i)
            start_index = str_data.index("$")
            while start_index + 1 < len(str_data) and str_data[start_index + 1] != "{":
                start_index = str_data.index("$", start_index + 1)
            # 从$开始往后找对应的}
            end_index = str_data.index("}", start_index)
            # yaml文件的参数，方法名（参数）
            ref_all_params = str_data[start_index:end_index + 1]
            print(ref_all_params)
            # 输出函数名称，${get_extract_data(token)}
            func_name = ref_all_params[2:ref_all_params.index("(")]
            print("取出的函数名称：", func_name)

            # 取出函数里的参数值
            func_params = ref_all_params[ref_all_params.index("(") + 1:ref_all_params.index(")")]
            print("取出函数名里面的参数：", func_params)

            # 传入替换的参数获取对应的值，*func_params，分隔重新得到一个字符串，python里面的反射，getattr()、setattr()、delattr()
            # *为解包运算符，把列表用*解包拆开为独立参数
            # getattr()根据字符串名字func_name动态拿到对象的方法DebugTalk()
            args = [x.strip() for x in func_params.split(',')] if func_params else []
            # 先实例化 DebugTalk 对象，再取func_name方法,args是参数列表，进行解包
            extract_data = getattr(DebugTalk(), func_name)(*args)
            print("提取的数据：{}".format(extract_data))

            if extract_data and isinstance(extract_data, list):
                extract_data = ','.join(e for e in extract_data)
            str_data = str_data.replace(ref_all_params, str(extract_data))
            print("通过解析后替换的数据：", str_data)

        # 把替换后的数据变为字符串
        if data and isinstance(data, dict):
            data = json.loads(str_data)
        else:
            data = str_data
        return data

    def specification_yaml(self, base_info, testcase):
        """
        把易读测试用例yaml翻译成python程序可执行动作的核心代码块
        yaml是测试用例声明
        specification_yaml是翻译器 + 执行流水线（测试用例的背后逻辑）
        1、拼接完整接口地址
        2、解析yaml中读取变量的动态变量（yaml中无法直接调用python中的方法，在接收到yaml文件后解析函数和参数进行调用读取值，用于接口关联）
        3、区分请求参数和框架控制字段
        4、调用requests发送http请求
        5、收集请求响应信息写入allure报告
        6、根据extract规则提取返回值、存入公共变量
        7、断言
        规范yaml测试用例的写法
        :param case_info: list类型，调试取case_info[0]-->dict
        :return:
        """
        case_info = dict(base_info, **testcase)
        cookies = None
        params_type = ['params', 'data', 'json']
        try:
            base_url = self.conf.get_envi('host')
            print(base_url)
            url = base_url + case_info.pop('url', None)
            allure.attach(url, f'接口地址：{url}')
            api_name = case_info.pop('api_name', None)
            allure.attach(api_name, f"接口名称：{api_name}")
            method = case_info.pop('method', None)
            allure.attach(method, f"请求方法：{method}")
            headers = case_info.pop('header', None)
            header_str = json.dumps(headers, ensure_ascii=False, indent=2)
            allure.attach(header_str, f"请求头：{header_str}", allure.attachment_type.TEXT)
            try:
                cookies = self.replace_load(case_info['cookies'])
                case_info.pop("cookies", None)
                if isinstance(cookies, str):
                    # 字符串"None" → None
                    if cookies.strip().upper() == "NONE":
                        cookies = None
                    # 字符串形式的字典，还原成dict
                    elif cookies.strip().startswith("{") and cookies.strip().endswith("}"):
                        try:
                            cookies = ast.literal_eval(cookies)
                        except Exception:
                            logs.warning(f"cookie字符串无法转为字典：{cookies}")
                            cookies = None
            except:
                pass

            case_name = case_info.pop('case_name', None)
            allure.attach(case_name, f"测试用例名称：{case_name}")
            validation = case_info.pop('validation', None)
            extract = case_info.pop('extract', None)
            # 如果提取得变量只有一个则返回None
            extract_list = case_info.pop('extract_list', None)

            # 处理文件上传接口
            file, files = case_info.pop('files', None), None
            if file is not None:
                for fk, fv in file.items():
                    allure.attach(json.dumps(file), "导入文件")
                    files = {fk: open(fv, mode="rb")}

            for key, value in case_info.items():
                if key in params_type:
                    case_info[key] = self.replace_load(value)

            res = self.send.run_main(api_name=api_name,
                                     url=url,
                                     case_name=case_name,
                                     headers=headers,
                                     method=method,
                                     cookies=cookies,
                                     files=files,
                                     **case_info)
            allure.attach(res.text, "接口的响应信息", allure.attachment_type.TEXT)
            allure.attach(str(res.status_code), f"接口状态码：{res.status_code}", allure.attachment_type.TEXT)
            res_text = res.text
            res_json = res.json()
            if extract is not None:
                self.extract_data(extract, res.text)
            if extract_list is not None:
                self.extract_data_list(extract_list, res.text)

            # 处理接口断言
            ass = Assertions()
            ass.assert_result(expected=validation, response=res_json, status_code=res.status_code)

        except Exception as e:
            logs.error(e)
            raise e

    def extract_data(self, testcase_extract, response):
        """
        将yaml需要提取的变量值保存到extract.yaml中
        :param testcase_extract: yaml文件中关键字extract的值
        :param response: 接口的实际返回值
        :return:
        """
        # 正则表达式类型
        pattenr_lst = ['(.+?)', '(.*?)', r'(\d+)', r'(\d*)']
        try:
            for key, value in testcase_extract.items():
                for pat in pattenr_lst:
                    if pat in value:
                        ext_list = re.search(value, response)
                        print(ext_list)
                        if pat in [r'(\d+)', r'(\d*)']:
                            extract_data = {key: int(ext_list.group(1))}
                        else:
                            extract_data = {key: ext_list.group(1)}
                        logs.info(f'正则表达式提取到的参数：{extract_data}')
                        self.read.write_yaml_data(extract_data)
                if "$" in value:
                    ext_json = jsonpath.jsonpath(json.loads(response), value)[0]
                    if ext_json:
                        extract_data = {key: ext_json}
                    else:
                        extract_data = {key: "未提取到数据，该接口返回值为空或者json提取表达式有误！"}
                    logs.info(f'json提取到的参数：{extract_data}')
                    self.read.write_yaml_data(extract_data)
        except Exception as e:
            logs.error("接口返回值提取异常，请检查yaml文件的extract表达式是否正确！")

    def extract_data_list(self, testcase_extract_list, response):
        """
        提取yaml文件的多个参数到extract.yaml文件中，提取结果以列表形式返回
        :param testcase_extract_list: yaml文件中的extract_list信息
        :param response: 接口的实际返回值，str类型
        :return:
        """
        try:
            for key, value in testcase_extract_list.items():
                if '(.+?)' in value or '(.*?)' in value:
                    # re.S作用是.为任意字符，包含换行，.匹配任意字符
                    ext_list = re.findall(value, response, re.S)
                    if ext_list:
                        extract_data = {key: ext_list}
                        logs.info('正则提取到的参数：%s' % extract_data)
                        self.read.write_yaml_data(extract_data)
                if "$" in value:
                    # 增加提取判断，有些返回结果为空提取不到，给一个默认值
                    ext_json = jsonpath.jsonpath(json.loads(response), value)
                    if ext_json:
                        extract_data = {key: ext_json}
                    else:
                        extract_data = {key: "未提取到数据，该接口返回结果可能为空"}
                    logs.info('json提取到参数：%s' % extract_data)
                    self.read.write_yaml_data(extract_data)
        except:
            logs.error('接口返回值提取异常，请检查yaml文件extract_list表达式是否正确！')


if __name__ == '__main__':
    req = RequestBase()
    data = get_testcase_yaml('../testcase/Login/login.yaml')[0]
    # print(f"data：{data}")
    # req.replace_load(data)
    req.specification_yaml(data)
