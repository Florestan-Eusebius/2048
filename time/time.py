import csv
import numpy as np
s='pointtimeA'
sum=[]
ave=[]
for i in range(10):
    f=open(s+str(2*i+2)+'.csv','r')
    reader=csv.reader(f)
    L=[float(i[0]) for i in reader]
    sum.append(np.sum(L))
    ave.append(np.mean(L))

print(sum)
print(np.mean(sum))
print(ave)
print(np.mean(ave))