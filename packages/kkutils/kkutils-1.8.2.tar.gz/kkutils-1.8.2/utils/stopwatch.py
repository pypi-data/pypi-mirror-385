#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Author:   root
Created:  2022-11-16 21:18:34
"""

import time
from datetime import timedelta


class Stopwatch:

    def __init__(self, start=False):
        self.duration = 0.0
        self.begin = None
        self.time = None
        if start:
            self.start()

    def reset(self):
        self.duration = 0.0
        self.start()

    def start(self):
        self.begin = time.time()

    def stop(self):
        delta = time.time() - self.begin
        self.duration += delta
        self.start()
        return delta

    def eta(self, size):
        if self.time is None:
            self.time = time.time()
            self.size = size
            self._eta = timedelta(seconds=-1)
        elif time.time() - self.time >= 10:
            consumed = self.size - size
            speed = consumed / (time.time() - self.time)
            if speed != 0:
                self.time = time.time()
                self.size = size
                self._eta = timedelta(seconds=int(size / speed))

        return self._eta
