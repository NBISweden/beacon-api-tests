"""
Queries that are not allowed according to the api spec
Check that the beacon does not allow these
"""
from .basequery import base


def no_refname():
    """ Check that queries without referenceName is not allowed """
    # Should give spec error and beacon error
    query = base()
    del query['referenceName']
    return query, {}


def no_refbases():
    """ Check that queries without referenceBases is not allowed """
    query = base()
    del query['referenceBases']
    return query, {}


def no_assembly():
    """ Check that queries without assemblyId is not allowed """
    query = base()
    del query['assemblyId']
    return query, {}


tests = [no_assembly, no_refbases, no_refname]
