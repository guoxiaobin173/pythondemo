import pytest
import allure

from base.generateId import m_id, c_id
from common.readyaml import get_testcase_yaml
from common.recordlog import logs
from common.sendrequest import SendRequest
from base.apiutil import RequestBase


@allure.feature(next(m_id) + '登录接口')
class TestLogin:
    # yaml返回的是列表，里面有多个测试数据，【baseinfo,ts】，所以接收的时候就是两个
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml('./testcase/Login/login.yaml'))
    @allure.story(next(c_id) + '用户名和密码登录校验')
    def test_login(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)
