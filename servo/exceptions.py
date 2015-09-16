# -*- coding: utf-8 -*-

class ServoException(Exception):
    """docstring for ServoException"""
    def __init__(self, arg):
        super(ServoException, self).__init__()
        self.arg = arg
        