'''
(c) 2017 Red Tech Research Corporation
This source code is released under the New BSD license.  Please see

Created on November 2017

@author: Romeo Demeterio
@contact: romeodemeteriojr@gmail.com
@summary: Understanding slicing and dicing of dimension arrays in Python
'''

import numpy as np

a = np.arange(30).reshape(2, 3, 5)
print a
print
print "a[0, 0, 0] --> ", a[0, 0, 0]
print "a[0, 0, 1] --> ", a[0, 0, 1]
print "a[0, 0, 2] --> ", a[0, 0, 2]
print "a[0, 0, 3] --> ", a[0, 0, 3]
print "a[0, 0, 4] --> ", a[0, 0, 4]


print "a[0, 0, :] --> ", a[0, 0, :]
print "a[0, :, :] --> ", a[0, :, :]
print "a[1, :, :] --> ", a[1, :, :]

print "a[:, 0, :] --> ", a[:, 0, :]
print "a[:, 1, :] --> ", a[:, 1, :]
print "a[:, 2, :] --> ", a[:, 2, :]

print "a[:, 1, 1] --> ", a[:, 1, 1]
print "a[:, 1, 1:3] --> ", a[:, 1, 1:3]
print "a[:, 1:, 1:3] --> ", a[:, 1:, 1:3]
print

print "np.sum(a, axis=0) --> ", np.sum(a, axis=0)
print "np.sum(a, axis=1) --> ", np.sum(a, axis=1)
print "np.sum(a, axis=2) --> ", np.sum(a, axis=2)
