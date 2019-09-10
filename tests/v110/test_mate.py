"""Testing breakends (aka BND, mates). Check that they work and that we get the expected output."""
from utils.beacon_query import call_beacon
from utils.compare import assert_partly_in, run_test


@run_test()
def test_search_1():
    """Test a mate query with referenceBases=N. This should give two answers, one for each direction."""
    query = {}
    query['start'] = 321680
    query['end'] = 123459
    query['referenceName'] = '2'
    query['mateName'] = '13'
    query['referenceBases'] = 'N'
    query['variantType'] = 'BND'
    query['assemblyId'] = 'GRCh38'
    query['includeDatasetResponses'] = 'HIT'
    resp = call_beacon(query=query)
    gold = {"datasetId": "GRCh38:beacon_test:2030-01-01",
            "referenceName": '2',
            "exists": True,
            "referenceBases": "G",
            "alternateBases": "G",
            "variantType": "BND"
            }
    gold2 = {"datasetId": "GRCh38:beacon_test:2030-01-01",
             "referenceName": '13',
             "exists": True,
             "referenceBases": "A",
             "alternateBases": "A",
             "variantType": "BND"
             }
    assert len(resp.get("datasetAlleleResponses", [])) == 2, \
        f'All allele responses not in response. Expected 2, found {len(resp.get("datasetAlleleResponses", []))}'
    assert_partly_in(gold, resp, 'datasetAlleleResponses')
    assert_partly_in(gold2, resp, 'datasetAlleleResponses')


@run_test()
def test_search_2():
    """Test a mate query with referenceBases set to A. This should only give one hit."""
    query = {}
    query['start'] = 123459
    query['end'] = 321680
    query['referenceName'] = '13'
    query['mateName'] = '2'
    query['referenceBases'] = 'A'
    query['variantType'] = 'BND'
    query['assemblyId'] = 'GRCh38'
    query['includeDatasetResponses'] = 'HIT'
    resp = call_beacon(query=query)
    gold = {"datasetId": "GRCh38:beacon_test:2030-01-01",
            "referenceName": "13",
            "exists": True,
            "referenceBases": "A",
            "alternateBases": "A",
            "variantType": "BND"
            }
    assert_partly_in(gold, resp, 'datasetAlleleResponses')
