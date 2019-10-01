"""
Queries that are not allowed according to the api spec.

Check that the beacon does not allow these
"""
from utils.beacon_query import call_beacon
from utils.compare import run_test


QUERY = {'referenceName': "22",
         'referenceBases': 'GG',
         'alternateBases': 'N',
         'assemblyId': 'GRCh38',
         'start': 0,
         'end': 2,
         'includeDatasetResponses': 'HIT',
         'datasetIds': ['GRCh38:beacon_test:2030-01-01']
         }


@run_test()
def no_refname():
    """Check that queries without referenceName is not allowed."""
    query = dict(QUERY)
    del query['referenceName']
    call_beacon(query=query, code=400, ignore_schemas=True)


@run_test()
def no_refbases():
    """Check that queries without referenceBases is not allowed."""
    query = dict(QUERY)
    del query['referenceBases']
    call_beacon(query=query, code=400, ignore_schemas=True)


@run_test()
def no_assembly():
    """Check that queries without assemblyId is not allowed."""
    query = dict(QUERY)
    del query['assemblyId']
    call_beacon(query=query, code=400, ignore_schemas=True)


@run_test()
def no_alternate():
    """Check that either alternateBases or variantType is required."""
    query = dict(QUERY)
    del query['alternateBases']
    call_beacon(query=query, code=400, ignore_schemas=True)


@run_test()
def start_and_startMin():
    """Check that you cannot use start and startMin+startMax."""
    query = dict(QUERY)
    query['startMin'] = 17301520
    query['startMax'] = 17301530
    query['endMin'] = 17301536
    query['endMax'] = 17301536
    query['referenceBases'] = 'A'
    call_beacon(query=query, code=400, ignore_schemas=True)


@run_test()
def no_start():
    """Check that you cannot query without start."""
    query = dict(QUERY)
    del query['start']
    query['referenceBases'] = 'A'
    call_beacon(query=query, code=400, ignore_schemas=True)
