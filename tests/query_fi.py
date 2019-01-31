""" Example tests for finnish beacon. Check that they work and that we get the expected output """
# TODO to be updated to actually use test suite. Currently using the swedish beacon as standard

from basequery import base
from utils.validate import validate_query


@validate_query(200, path='/')
def info():
    return {}, {}


@validate_query(200)
def test_fi():
    """ Test variantTypes snp """
    query = base()
    query['start'] = 36585457
    query['end'] = 0
    query['variantType'] = 'INS'
    query['referenceBases'] = 'A'
    query['referenceName'] = 19
    query['assemblyId'] = 'GRCh99'
    del query['alternateBases']
    resp = {"datasetAlleleResponses": [
             {"datasetId": "urn:hg:1000genome",
              "referenceName": "19",
              "variantCount": 419,
              "callCount": 5008,
              "sampleCount": 2504,
              "exists": True,
              "referenceBases": "A",
              "alternateBases": "AAAT",
              "variantType": "INS",
              "frequency": 0.083666131,
              },
              {
              "datasetId": "urn:hg:1000genome",
              "referenceName": "19",
              "externalUrl": "ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/",
              "variantCount": 19,
              "callCount": 5008,
              "sampleCount": 2504,
              "exists": True,
              "referenceBases": "A",
              "alternateBases": "AAATAAT",
              "variantType": "INS",
              "frequency": 0.00379393,
              }]}
    return query, resp
