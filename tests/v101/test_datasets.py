"""Tests for more than one dataset."""

from utils.beacon_query import call_beacon
from utils.compare import assert_partly_in, assert_not_in, run_test


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
def test_two_datasets():
    """Test that both datasets repsond."""
    query = dict(QUERY)
    query['start'] = 16577043
    query['end'] = 16577045
    query['referenceBases'] = 'TG'
    del query['alternateBases']
    query['variantType'] = 'SNP'
    del query['datasetIds']
    resp = call_beacon(query=query)
    assert len(resp.get("datasetAlleleResponses", [])) > 1, 'All datasets not in response'
    gold = {"datasetId": "GRCh38:beacon_test:2030-01-01",
            "referenceName": "22",
            "callCount": 5008,
            "variantCount": 17,
            "sampleCount": 2504,
            "exists": True,
            "referenceBases": "TG",
            "alternateBases": "AG",
            "variantType": "SNP",
            "frequency": 0.003394569
            }
    gold2 = {"datasetId": "GRCh38:beacon_test2:2030-01-01",
             "referenceName": "22",
             "exists": True,
             "referenceBases": "TG",
             "alternateBases": "AG",
             "variantType": "SNP",
             "start": 16577043,
             "end": 16577045,
             "frequency": 0.003394569,
             "variantCount": 17,
             "callCount": 5008,
             "sampleCount": 2504
             }
    assert_partly_in(gold, resp, 'datasetAlleleResponses')
    assert_partly_in(gold2, resp, 'datasetAlleleResponses')


@run_test()
def test_second_datasets():
    """Test that excluding a dataset works."""
    query = dict(QUERY)
    query['start'] = 16577043
    query['end'] = 16577045
    query['referenceBases'] = 'TG'
    del query['alternateBases']
    query['variantType'] = 'SNP'
    query['datasetIds'] = ["GRCh38:beacon_test2:2030-01-01"]
    resp = call_beacon(query=query)
    assert len(resp.get("datasetAlleleResponses", [])) == 1, \
        f'Response should include exactly 1 dataset, found {len(resp.get("datasetAlleleResponses", []))}'
    exclude = {"datasetId": "GRCh38:beacon_test:2030-01-01"}
    assert_not_in(exclude, resp, 'datasetAlleleResponses')


@run_test()
def test_datasets_info():
    """Test that both datasets are in the beacon's info (/) call."""
    resp = call_beacon(path='/')
    gold = {"id": "GRCh38:beacon_test:2030-01-01",
            "assemblyId": "GRCh38",
            "variantCount": 17,
            "callCount": 12,
            "sampleCount": 2504
            }
    gold2 = {"id": "GRCh38:beacon_test2:2030-01-01",
             "assemblyId": "GRCh38",
             "variantCount": 17,
             "callCount": 12,
             "sampleCount": 2504
             }
    assert len(resp.get("datasets", [])) > 1, \
        f'All datasets not in response. Expected 2, found {len(resp.get("datasets", []))}'
    assert_partly_in(gold, resp, 'datasets')
    assert_partly_in(gold2, resp, 'datasets')
