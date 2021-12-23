# ddd = {}
# for i in range(5):
#     ddd[i] = i+10
#
# for j in ddd.values():
#     print(j)

import numpy as np

# ccc = { "一": {1 : 123}, "二" : {2 : 223}}
# for i in ccc:
#     print(i)
#
# print(len(ccc))
#
# print('===========')
#
# aaa = np.ones(shape=[4,5])
#
# print(len(aaa[:,1]))

import json

cur_flow = {}
cur_flow[1] = "curflow1"
cur_flow['2'] = "curflow2"
cur_flow['3'] = "curflow3"
cur_flow['4'] = "curflow4"

str1 = json.dumps(cur_flow)
print(str1)
print(type(str1))