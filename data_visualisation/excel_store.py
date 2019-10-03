import os
import shutil
import time
from util.project_root import get_project_root

from xlwt import Workbook


class ExcelPrinter(object):

    def __init__(self, x_size, y_size, x_range=30, y_range=30):
        self.wb = Workbook()
        self.sheet = self.wb.add_sheet('results')
        self.x_range = x_range
        self.y_range = y_range
        self.x_size = x_size
        self.y_size = y_size
        self.fillstandarddata()

    def fillstandarddata(self):
        """"this method fills the xls sheet with the correct layout and the data that is possible
        to fill in (data, beginning time)"""
        self.sheet.write(0, 0, "Date:")
        self.sheet.write(0, 1, time.strftime("%Y-%m-%d", time.gmtime()))
        self.sheet.write(1, 0, "Begin time:")
        self.sheet.write(1, 1, time.strftime("%H:%M:%S", time.gmtime()))
        self.sheet.write(2, 0, "End time:")
        self.sheet.write(3, 0, "Execution Time: ")
        self.sheet.write(4, 0, "x-range")
        self.sheet.write(5, 0, "y-range")
        self.sheet.write(4, 1, self.x_range)
        self.sheet.write(5, 1, self.y_range)
        self.sheet.write(6, 0, "x step size")
        self.sheet.write(7, 0, "y step size")
        self.sheet.write(6, 1, self.x_size)
        self.sheet.write(7, 1, self.y_size)
        self.sheet.write(8, 0, "data interpretation")
        self.sheet.write(9, 0, "row: horizontal scan")
        self.sheet.write(10, 0, "Column: vertical scan")
        self.sheet.write(11, 0, "Remarks")

    def fillresults(self, values):
        # fill the 30x30 grid
        size = values.shape
        xsize, ysize = size
        for x in range(xsize):
            for y in range(13, ysize + 13):
                self.sheet.write(y, x, str(values[x][y - 13]))

    def end(self, begintime, endtime, values, remark=None):
        self.fillresults(values)
        excecutiontime = endtime - begintime
        excecutiontime = excecutiontime / 60
        self.sheet.write(2, 1, time.strftime("%H:%M:%S", time.gmtime(endtime)))
        self.sheet.write(3, 1, str(excecutiontime) + "minutes")

        # ask the user for input on remarks
        self.sheet.write(11, 1, remark)
        self.save(remark)

    def save(self, remark):
        """"method to save the xls file and move it to the correct directory"""
        # get the current time
        timestring = self.reformattime()
        print(timestring)
        print(remark)
        # name te file after the current time with the correct format
        self.wb.save(remark)

        # get the relative path so it works on all operating systems
        rel_path = get_project_root()
        folder_path = os.path.join(rel_path, "data_visualisation", "ExcelFiles" + "\\" "scan_files")
        print(folder_path)
        # move the file to the correct folder
        shutil.move(remark, folder_path)

    def reformattime(self):
        """"returns the time in UTC defined as year-month-day-hour:minute:second. Time is the UTC time"""
        return time.strftime("%Y-%m-%d-%H,%M,%S-UTC-Grindscan.xls", time.gmtime())
