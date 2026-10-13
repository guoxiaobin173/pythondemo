import pytest
import allure

from base.generateId import m_id, c_id
from common.readyaml import get_testcase_yaml
from common.recordlog import logs
from common.sendrequest import SendRequest
from base.apiutil import RequestBase


@allure.feature(next(m_id) + '商品管理')
class TestProductList:
    @allure.story(next(c_id) + '成功获取商品列表')
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml('./testcase/productManage/getProductList.yaml'))
    def test_get_product_list(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)

    @allure.story(next(c_id) + '成功获取商品详情信息')
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml('./testcase/productManage/productDetail.yaml'))
    def test_get_product_detail(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)

    @allure.story(next(c_id) + '商品正常提交订单')
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml('./testcase/productManage/placeAnOrder.yaml'))
    def test_place_an_order(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)

    @allure.story(next(c_id) + '正常订单支付')
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml('./testcase/productManage/orderPay.yaml'))
    def test_order_pay(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)

    @allure.story(next(c_id) + '成功添加商品到购物车')
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml('./testcase/productManage/shoppingJoinCart.yaml'))
    def test_shopping_join_cart(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)

    @allure.story(next(c_id) + '正常校验商品订单状态')
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml('./testcase/productManage/checkOrderStatus.yaml'))
    def test_check_order_status(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)

    @allure.story(next(c_id) + '正常校验商品物流状态接口')
    @pytest.mark.parametrize('base_info,testcase',
                             get_testcase_yaml('./testcase/productManage/checkLogisticsStatus.yaml'))
    def test_check_logistics_status(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)

    @allure.story(next(c_id) + '正常校验商品库存')
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml('./testcase/productManage/shoppingInventory.yaml'))
    def test_product_inventory(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)
