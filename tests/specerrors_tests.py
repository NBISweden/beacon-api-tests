"""
Queries that are not allowed according to the api spec
Check that the beacon does not allow these
"""
from tests.basequery import base
from utils.validate import validate_query


@validate_query(400, test_query=False)
def no_refname():
    """ Check that queries without referenceName is not allowed """
    # Should give spec error and beacon error
    query = base()
    del query['referenceName']
    return query, {}


@validate_query(400, test_query=False)
def no_refbases():
    """ Check that queries without referenceBases is not allowed """
    query = base()
    del query['referenceBases']
    return query, {}


@validate_query(400, test_query=False)
def no_assembly():
    """ Check that queries without assemblyId is not allowed """
    query = base()
    del query['assemblyId']
    return query, {}
