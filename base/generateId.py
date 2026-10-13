def generate_module_id():
    """
    生成测试模块编号，保证allure报告按pytest设定的执行顺序执行
    :return:
    """
    for i in range(1, 1000):
        module_id = 'M' + str(i).zfill(2) + '_'
        # 返回后会接着前面的执行
        yield module_id

def generate_testcase_id():
    """
    生成测试用例编号
    :return:
    """
    for i in range(1, 10000):
        case_id = 'C' + str(i).zfill(2) + '_'
        yield case_id


m_id = generate_module_id()
c_id = generate_testcase_id()
