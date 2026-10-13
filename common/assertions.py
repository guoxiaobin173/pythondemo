import operator
import os.path
import allure
import jsonpath
from common.readyaml import get_testcase_yaml
from common.recordlog import logs
from common.connectdb import ConnectMysql


class Assertions:
    """
    接口断言模式封装，支持
    1、字符串包含
    2、结果不相等断言
    3、结果相等断言
    4、断言接口返回值里面的任意一个值
    5、数据库断言
    """

    def contains_assert(self, value, response, status_code):
        """
        字符串包含断言：断言预期结果的字符串是否包含在接口的实际返回结果中
        :param value: 预期结果yaml文件中validation关键字下的结果
        :param response:
        :param status_code:
        :return:
        """
        # 断言状态标识，0代表成功，其他代表失败
        flag = 0
        if isinstance(value, dict) and isinstance(response, dict):
            for assert_key, assert_value in value.items():
                if assert_key == "status_code":
                    if assert_value != status_code:
                        flag += 1
                        logs.error("contains断言失败，接口返回码【%s】不等于【%s】" % (status_code, assert_value))
                    else:
                        logs.info("contains断言成功：预期结果：【%s】，实际结果：【%s】" % (status_code, assert_value))
                    continue
                # $..递归向下搜索key
                res_list = jsonpath.jsonpath(response, '$..%s' % assert_key)
                # jsonpath找不到匹配会返回None，必须先判断
                if res_list is None:
                    flag += 1
                    logs.error(f"contains断言失败：未找到字段【{assert_key}】")
                    continue
                # 原逻辑：字符串包含。如果提取出来是字符串，直接做in；如果是其他类型，转为字符串再做包含匹配
                real_val = res_list[0]
                if isinstance(real_val, str):
                    real_str = real_val
                else:
                    real_str = str(real_val)

                if assert_value in real_str:
                    logs.info("字符串断言成功：预期结果：【%s】，实际结果：【%s】" % (assert_value, real_str))
                else:
                    flag += 1
                    logs.error(f"响应文本断言失败：预期结果为：【%s】，实际结果为：【%s】" % (assert_value, real_str))
        else:
            raise TypeError("contains断言失败--类型错误，预期结果和接口的实际响应结果必须为字典类型")
        return flag

    def equal_assert(self, value, response):
        """相等断言：只校验yaml里写的key，不修改原始response对象"""
        flag = 0
        if isinstance(value, dict) and isinstance(response, dict):
            resp_copy = {}
            for assert_key in value.keys():
                if assert_key in response:
                    resp_copy[assert_key] = response[assert_key]
                else:
                    flag += 1
                    logs.error(f"相等断言失败：响应中不存在key【{assert_key}】")
            eq_assert = operator.eq(resp_copy, value)
            if eq_assert:
                logs.info(f"相等断言成功：接口的实际结果为：{resp_copy}，等于预期结果：{str(value)}")
            else:
                flag += 1
                logs.error(f"相等断言失败：接口的实际结果为：{resp_copy}，不等于预期结果：{str(value)}")
        else:
            raise TypeError("equal断言失败--类型错误，预期结果和接口的实际响应结果必须为字典类型")
        return flag

    def not_equal_assert(self, value, response):
        """
        不相等断言，不相等才是断言成功
        :param value:
        :param response:
        :return:
        """
        flag = 0
        if isinstance(value, dict) and isinstance(response, dict):
            resp_copy = {}
            for assert_key in value.keys():
                if assert_key in response:
                    resp_copy[assert_key] = response[assert_key]
                else:
                    flag += 1
                    logs.error(f"不相等断言失败：响应中不存在key【{assert_key}】")
            eq_assert = operator.ne(resp_copy, value)
            if eq_assert:
                logs.info(f"不相等断言成功：接口的预期结果：{str(value)}，不等于实际结果为：{resp_copy}")
            else:
                flag += 1
                logs.error(f"不相等断言失败：接口的预期结果：{str(value)}，等于实际结果为：{resp_copy}")
        else:
            raise TypeError("not_equal断言失败--类型错误，预期结果和接口的实际响应结果必须为字典类型")
        return flag

    def assert_mysql(self, expected_sql):
        """
        数据库断言
        :param expected_sql: 预期结果，也就是yaml文件中的sql语句
        :return:
        """
        flag = 0
        conn = ConnectMysql()
        db_value = conn.query(expected_sql)
        if db_value is not None:
            logs.info("数据库断言成功")
        else:
            flag += 1
            logs.error("数据库断言失败，检查数据库是否存在该数据")
        return flag

    def assert_result(self, expected, response, status_code):
        """
        断言模式，通过all_flag标记断言结果
        :param expected: 预期结果
        :param response: 接口实际返回结果（json格式）
        :param status_code: 响应状态码
        :return:
        """
        all_flag = 0
        try:
            # expected是预期结果列表
            for yq in expected:
                # yq是字典，{'contains':{'msg':'登录成功'}}
                for key, value in yq.items():
                    # value是{'msg':'登录成功'}
                    if key == "contains":
                        flag = self.contains_assert(value, response, status_code)
                    elif key == "eq":
                        flag = self.equal_assert(value, response)
                    elif key == "ne":
                        flag = self.not_equal_assert(value, response)
                    elif key == "db":
                        flag = self.assert_mysql(value)
                    else:
                        flag = 0
                    all_flag += flag
            assert all_flag == 0
            logs.info("测试成功！")
        except Exception as e:
            logs.error("测试失败！")
            logs.error(f"异常信息：{e}")
            assert all_flag == 0


if __name__ == '__main__':
    data = get_testcase_yaml(os.path.join(os.path.dirname(os.path.dirname(__file__)), r'testcase\Login\login.yaml'))[0]
    value = data['testCase']['validation']
    response = {"error_code": None, "msg": "登录成功", "msg_code": 200, "orgId": "6140913758128971280",
                "token": "2aE2bbDD66D35f5EEda77CE7abe70", "userId": "9337151637697210487"}
    ass = Assertions()
    for i in value:
        for j, k in i.items():
            ass.equal_assert(value=k, response=response)
