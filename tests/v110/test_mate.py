"""Example tests. Check that they work and that we get the expected output."""
from utils.validate import validate_query


@validate_query(200)
def test_search_1():
    """Test a mate query with referenceBases=N. This should give two answers, one for each direction."""
    query = {}
    query['start'] = 321681
    query['end'] = 123460
    query['referenceName'] = '2'
    query['mateName'] = '13'
    query['referenceBases'] = 'N'
    query['variantType'] = 'BND'
    query['assemblyId'] = 'GRCh38'
    query['includeDatasetResponses'] = 'HIT'
    resp = {"datasetAlleleResponses": [
        {"datasetId": "GRCh38:beacon_test:2030-01-01",
         "referenceName": '2',
         "exists": True,
         "referenceBases": "G",
         "alternateBases": "G",
         "variantType": "BND"
         },
        {"datasetId": "GRCh38:beacon_test:2030-01-01",
         "referenceName": '13',
         "exists": True,
         "referenceBases": "A",
         "alternateBases": "A",
         "variantType": "BND"
         }]}
    return query, resp


@validate_query(200)
def test_search_2():
    """Test a mate query with referenceBases set to A. This should only give one hit."""
    query = {}
    query['start'] = 123460
    query['end'] = 321681
    query['referenceName'] = '13'
    query['mateName'] = '2'
    query['referenceBases'] = 'A'
    query['variantType'] = 'BND'
    query['assemblyId'] = 'GRCh38'
    query['includeDatasetResponses'] = 'HIT'
    resp = {"datasetAlleleResponses": [
        {"datasetId": "GRCh38:beacon_test:2030-01-01",
         "referenceName": "13",
         "exists": True,
         "referenceBases": "A",
         "alternateBases": "A",
         "variantType": "BND"
         }]}
    return query, resp
