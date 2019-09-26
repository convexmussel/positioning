import numpy
import csv

def read_file():
    data_path = r'C:\Users\Jarno\Dropbox\nano\APT_Piezo-master\data_visualisation\ExcelFiles\2019-08-29-10,54,04-UTC-Grindscan.csv'
    with open(data_path, 'r') as f:
        reader = csv.reader(f, delimiter=';')
        # get header from first row
        headers = next(reader)
        # get all the rows as a list
        data = list(reader)
        # transform data into numpy array
        data = numpy.array(data).astype(float)
    return data

