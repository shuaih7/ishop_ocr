import os, sys
import numpy as np

A = np.array([1,2,3,4,5])
print(type(A))

if isinstance(A, np.ndarray): print("Yeah!")