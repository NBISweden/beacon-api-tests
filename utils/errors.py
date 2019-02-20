""" Test suite errors """


class BeaconTestError(Exception):
    """ Class for all exceptions that are expected """
    def __init__(self):
        Exception.__init__(self)
