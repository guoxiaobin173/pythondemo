# 文件路径
import logging
import os.path
import sys

# __file__代表当前py文件的完整绝对路径，os.path.dirname(path)用于截取传入路径的上一级文件目录
# DIR_BASE就是项目根目录pytestdemo下
DIR_BASE = os.path.dirname(os.path.dirname(__file__))
sys.path.append(DIR_BASE)

# log日志输出级别
LOG_LEVEL = logging.DEBUG  # 文件
STREAM_LOG_LEVEL = logging.DEBUG  # 控制台

# 接口超时时间，单位s
API_TIMEOUT = 60

# excel文件的sheet页，默认读取第一页
SHEET_ID = 0

# 生成测试报告类型
REPORT_TYPE = 'allure'

# 是否发送钉钉消息
dd_msg = False

# os.path.join(a,b)为路径a和b的拼接函数
FILE_PATH = {
    'CONFIG': os.path.join(DIR_BASE, 'conf/config.ini'),
    'LOG': os.path.join(DIR_BASE, 'logs'),
    'YAML': os.path.join(DIR_BASE),
    'TEMP': os.path.join(DIR_BASE, 'report/temp'),
    'TMR': os.path.join(DIR_BASE, 'report/tmreport'),
    'EXTRACT': os.path.join(DIR_BASE, 'extract.yaml'),
    'XML': os.path.join(DIR_BASE, 'data/sql'),
    'RESULTXML': os.path.join(DIR_BASE, 'report'),
    'EXCEL': os.path.join(DIR_BASE, 'data', '测试数据.xls')
}

# 默认请求头信息
LOGIN_HEADER = {
    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive'
}
