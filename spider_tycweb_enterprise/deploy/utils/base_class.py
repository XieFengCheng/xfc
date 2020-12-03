#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------
describe:
    

--------------------------------------------------------------
"""

# ------------------------------------------------------------
# usage: /usr/bin/python base_class.py
# ------------------------------------------------------------
import threading


class BASECLASS(object):

    _instance = None
    _instance_lock = threading.Lock()

    def __init__(self):
        super(BASECLASS, self).__init__()
        self.init_run()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with BASECLASS._instance_lock:
                cls._instance = object.__new__(cls)
        return cls._instance

    def init_run(self):
        pass



