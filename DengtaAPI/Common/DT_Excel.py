#encoding=utf8
'''
Created on 2015-12-14

@author: johnson
'''
import xlrd,sys
from xlutils.copy import copy

def open_excel(file):
    try:
        data = xlrd.open_workbook(file)
#         table = data.sheets()[0]
        return data
    except Exception as e:
        print("Open excel fail :" +str(e))
        sys.exit()

def getColumnDataByName(file ,columnNameList):
    data= open_excel(file)
    table = data.sheet_by_name(u'Sheet1')
    nrows = table.nrows  # 行数
    ncols = table.ncols  # 列数
    if nrows==0 or ncols==0:
        print("table data error")

    result={}
    colnames = table.row_values(0)
    for columnName in columnNameList:
        if columnName in colnames:
            col_index= colnames.index(columnName)
        else:
            print(columnName + " not in table!")
            sys.exit()

        coldata= table.col_values(col_index)
        coldata.remove(columnName)
        new_list = [x for x in coldata if x != '']

        result[columnName]=new_list
    return result


def updateDataByColumnName(file, columnName, rowindex, value):
    try:
        data = xlrd.open_workbook(file, formatting_info=True)
    except Exception as e:
        print(str(e))
        sys.exit()

    table = data.sheet_by_name(u'Sheet1')
    nrows = table.nrows  # 行数
    ncols = table.ncols  # 列数
    if nrows == 0 or ncols == 0:
        print("table data error")

    colnames = table.row_values(0)
    if columnName in colnames:
        col_index = colnames.index(columnName)
    else:
        print(columnName + " not in table!")
        sys.exit()

    edit_data = copy(data)
    edit_sheet = edit_data.get_sheet(0)

    edit_sheet.write(rowindex, col_index, value)
    edit_data.save(file)

def updateColumnByColumnName(file, columnName, listValue):
    try:
        data = xlrd.open_workbook(file, formatting_info=True)
    except Exception as e:
        print(str(e))
        sys.exit()

    table = data.sheet_by_name(u'Sheet1')
    nrows = table.nrows  # 行数
    ncols = table.ncols  # 列数
    if nrows == 0 or ncols == 0:
        print("table data error")

    colnames = table.row_values(0)
    if columnName in colnames:
        col_index = colnames.index(columnName)
    else:
        print(columnName + " not in table!")
        sys.exit()

    edit_data = copy(data)
    edit_sheet = edit_data.get_sheet(0)

    for i in range(0,len(listValue)):
        edit_sheet.write(i+1, col_index, listValue[i])
    edit_data.save(file)