
import numpy
import pandas as pd
from piezo.interface.interfaces import interfaces
from piezo.interface.apt.apt import APT
import time
interface = interfaces()
newDF = pd.DataFrame()
newDF.columms = ["Laser current", "photodiode current"]
begin_time = time.time()
read_values = interface.read()

while begin_time+1800 > time.time():
    read_values = interface.read()

    newDF= newDF.append({'Laser current' : read_values[1] , 'photodiode current' : read_values[7]} , ignore_index=True)
    print(newDF)
    newDF.to_excel("results piezo 2.xlsx")
    time.sleep(1)
