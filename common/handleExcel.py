import os

import xlrd
import xlwt
from xlutils.copy import copy

from common.recordlog import logs
from conf import setting
from conf.setting import DIR_BASE


class HandleExcel:
    def __init__(self, file_path=None):
        if file_path is not None:
            self.file_path = file_path
        else:
            self.file_path = setting.FILE_PATH['EXCEL']
        self.__global_table = self.xls_obj()

    def xls_obj(self):
        """获取excel文件的对象，后续都通过该对象操作文件数据"""
        if os.path.splitext(self.file_path)[-1] != '.xlsx':
            obj = xlrd.open_workbook(self.file_path, formatting_info=True)
            xls_obj = obj.sheets()[0]
            return xls_obj
        else:
            logs.error('Excel文件格式必须是.xls格式！')

    def get_cols(self):
        """获取Excel的总列数"""
        return self.__global_table.ncols

    def get_rows(self):
        """获取excel的总行数"""
        return self.__global_table.nrows

    def get_cell_value(self, row, col):
        """
        获取单元格参数
        :return:
        """
        return self.__global_table.cell_value(row, col)

    def get_each_line(self, row):
        """
        获取excel一整行数据
        :param row:
        :return:
        """
        rows_data = self.__global_table.row_values(row)
        return rows_data

    def get_each_colum(self, col):
        """
        获取excel一整列数据
        :param col:
        :return:
        """
        cols_data = self.__global_table.col_values(col)
        return cols_data

    def write_xls_value(self, row, col, value):
        """
        往excel写入数据
        :param row:
        :param col:
        :param value:
        :return:
        """

        init_table = xlrd.open_workbook(self.file_path,formatting_info=True)
        copy_table = copy(init_table)
        sheet = copy_table.get_sheet(0)
        sheet.write(row, col, value)
        copy_table.save(self.file_path)

if __name__ == '__main__':
    handle = HandleExcel()
    # res = handle.get_cell_value(1, 4)
    # res = handle.get_each_line(0)
    res = handle.write_xls_value(2,1,'/dar/user/login')
    print(res)
