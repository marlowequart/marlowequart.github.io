
import re

date='1950-01-13'
date_mo=re.findall(r'-(.+?)-',date)[0]

print(date)
print(date_mo)
