# -*- coding: utf-8 -*-


class ConfigurationError(Exception):
    def __init__(self, arg):
        super(ConfigurationError, self).__init__(arg)


class InventoryAlreadyAtLocation(Exception):
    def __init__(self, arg):
        super(InventoryAlreadyAtLocation, self).__init__(arg)
