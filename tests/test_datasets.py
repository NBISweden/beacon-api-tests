"""Tests for more than one dataset."""

from tests.basequery import base
from utils.validate import validate_query, exclude_from_response


@validate_query(200)
def test_two_datasets():
    """Test that both datasets repsond."""
    query = base()
    query['start'] = 16577044
    query['end'] = 16577045
    query['referenceBases'] = 'T'
    del query['alternateBases']
    query['variantType'] = 'SNP'
    del query['datasetIds']
    resp = {"datasetAlleleResponses": [
        {"datasetId": "GRCh38:beacon_test:2030-01-01",
         "referenceName": "22",
         "callCount": 5008,
         "variantCount": 17,
         "sampleCount": 2504,
         "exists": True,
         "referenceBases": "T",
         "alternateBases": "A",
         "variantType": "SNP",
         "frequency": 0.003394569
         },
        {"datasetId": "GRCh38:beacon_test2:2030-01-01",
         "referenceName": "22",
         "externalUrl": "www.beacon.com",
         "exists": True,
         "referenceBases": "T",
         "alternateBases": "A",
         "variantType": "SNP",
         "start": 16577043,
         "end": 16577044,
         "frequency": 0.003394569,
         "variantCount": 17,
         "callCount": 5008,
         "sampleCount": 2504
         }]}
    return query, resp


@exclude_from_response()
def test_second_datasets():
    """Test that excluding a dataset works."""
    query = base()
    query['start'] = 16577044
    query['end'] = 16577045
    query['referenceBases'] = 'T'
    del query['alternateBases']
    query['variantType'] = 'SNP'
    query['datasetIds'] = "GRCh38:beacon_test2:2030-01-01"
    resp = {"datasetAlleleResponses": [{"datasetId": "GRCh38:beacon_test:2030-01-01"}]}
    return query, resp


@validate_query(200, path='/')
def test_info():
    """Test that both datasets are in the beacon's info (/) call."""
    resp = {'datasets': [
        {"id": "GRCh38:beacon_test:2030-01-01",
         "assemblyId": "GRCh38",
         "variantCount": 17,
         "callCount": 13,
         "sampleCount": 2504
         },
        {"id": "GRCh38:beacon_test2:2030-01-01",
         "assemblyId": "GRCh38",
         "variantCount": 4,
         "callCount": 2,
         "sampleCount": 2504
         }]}
    return {}, resp
