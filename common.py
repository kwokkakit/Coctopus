#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import random
import sys, os
import time


class BaseFunction():
    def __init__(self):
        pass

    def exportToFile(self):
        pass

    def format(self, str):
        return str.replace('\t', '').replace('\n', '').replace(' ', '')

    def sleep(self):
        i = random.randint(0, 5)
        print "Sleep " + str(i) + " seconds."
        time.sleep(i)
