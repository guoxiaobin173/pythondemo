import allure
import pytest

from base.generateId import m_id, c_id
from common.readyaml import get_testcase_yaml
from base.apiutil import RequestBase


@allure.feature(next(m_id) + "物流管理")
class TestLogistics:
    @allure.story(next(c_id) + "获取下单材料")
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml("./testcase/logisticsManage/getMaterial.yaml"))
    def test_get_material(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)

    @allure.story(next(c_id) + "货主创建订单")
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml("./testcase/logisticsManage/commitOrder.yaml"))
    def test_commit_order(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)

    @allure.story(next(c_id) + "总调集团接单")
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml("./testcase/logisticsManage/receiveOrder.yaml"))
    def test_receive_order(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)

    @allure.story(next(c_id) + "总调集团分配订单")
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml("./testcase/logisticsManage/assignOrder.yaml"))
    def test_assign_order(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)

    @allure.story(next(c_id) + "物流公司接单")
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml("./testcase/logisticsManage/getOrder.yaml"))
    def test_get_order(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)
