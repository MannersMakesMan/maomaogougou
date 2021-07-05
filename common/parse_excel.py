import os
import xlrd


def parse_excel(excel_path):
    # 解析xlsx文件 返回 [# 行1 {表头1: 数据, 表头2: 数据}, # 行2 {}, # 行3 {}]格式数据
    # file_name = os.path.join(os.getcwd(), excel_path)
    try:
        work_book = xlrd.open_workbook(excel_path)
    except xlrd.biffh.XLRDError as e:
        return []
    except Exception as e:
        return False
    work_sheet = work_book.sheet_by_index(0)

    # 获取总行数
    total_rows = work_sheet.nrows

    data_list = []
    key_list = None
    for i in range(total_rows):
        row_data = work_sheet.row_values(i)
        if i == 0:
            key_list = row_data
        else:

            data_dict = dict()
            for index, cel_data in enumerate(row_data):
                key = key_list[index]
                data_dict[key] = cel_data
            data_list.append(data_dict)
    if key_list:
        if not data_list:  # 只有一行数据的情况 第一行为表头
            data_list.append({i: '' for i in key_list})

    return data_list


if __name__ == '__main__':
    parse_excel('/root/project/automatic_test_system/工作簿1.xlsx')
