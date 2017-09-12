

from xlrd import open_workbook
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


xl_workbook = open_workbook('/home/bioinfo/mparker/work/20160615/excel_data/data_v2.xls')
xl_sheet = xl_workbook.sheet_by_index(0)
num_cols = xl_sheet.ncols   # Number of columns

costs = {}

for row_idx in range(1, xl_sheet.nrows):    # Iterate through rows
    # print ('-'*40)
    # print ('Row: %s' % row_idx)   # Print row number

    id = xl_sheet.cell(row_idx, 0).value
    #print ('Column: [%s] cell_obj: [%s]' % (0, cell_obj))

    if id not in costs:
        costs[id] = []

    cost = xl_sheet.cell(row_idx, 4).value
    #print ('Column: [%s] cell_obj: [%s]' % (4, cell_obj))

    costs[id].append(cost)

    # for col_idx in range(0, num_cols):  # Iterate through columns
    #     cell_obj = xl_sheet.cell(row_idx, col_idx)  # Get cell object by row, col
    #     print ('Column: [%s] cell_obj: [%s]' % (col_idx, cell_obj))




xl_sheet = xl_workbook.sheet_by_index(1)
num_cols = xl_sheet.ncols   # Number of columns

header = []

for row_idx in range(0, 1):    # Iterate through rows
    for col_idx in range(0, num_cols):  # Iterate through columns
        cell_obj = xl_sheet.cell(row_idx, col_idx).value  # Get cell object by row, col
        header.append(cell_obj)

header.append("total_summed_cost")
print ",".join(header)

for row_idx in range(2, xl_sheet.nrows):    # Iterate through rows
    # print ('-'*40)
    # print ('Row: %s' % row_idx)   # Print row number

    values = []

    id = xl_sheet.cell(row_idx, 0).value

    if id in costs:
        cost = sum(costs[id])
    else:
        cost = ""
    for col_idx in range(0, num_cols):  # Iterate through columns
        cell_obj = xl_sheet.cell(row_idx, col_idx).value  # Get cell object by row, col
        values.append("\"" + str(cell_obj) + "\"")
    values.append(str(cost))
    print ",".join(x for x in values)

