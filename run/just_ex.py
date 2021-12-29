import numpy as np

import numpy as np
a = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
b = np.array([1, 3, 6, 1, 9, 1, 5, 2, 9, 9])
c = np.array([[0, 3, 6, 1, 9],[0, 0, 2, 9, 9]])
for i in range(c.shape[0]):
    print(np.nonzero(c[i][:]))
# print(np.nonzero(c))