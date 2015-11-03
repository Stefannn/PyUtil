'''
Simple Timer for Python Code
@author Stefan Hegglin
'''
from __future__ import division
import time
import numpy as np

class Timer(object):
    '''Uses time.time() bc timer.clock() doesn't work with GPU/...'''
    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.interval_s = self.end - self.start

