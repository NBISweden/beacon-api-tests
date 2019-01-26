""" Example tests. Check that they work and that we get the expected output """
# TODO to be updated to actually use test suite. Currently using the swedish beacon as standard

from .basequery import base



def test_deletion():
    """ Test variantTypes deletion """
    query = base()
    query['start'] = 85177351
    query['end'] = 85177353
    query['variantType'] = 'DEL'
    query['referenceBases'] = 'CT'
    del query['alternateBases']
    resp = {"datasetAlleleResponses":
             [{"datasetId": "GRCh37p13:SweGen:20180409",
               "referenceName": "1",
               "callCount": 2000,
               "variantCount": 1,
               "sampleCount": 1000,
               "exists": True,
               "referenceBases": "CT",
               "alternateBases": "C",
               "variantType": "DEL",
               "frequency": 0.0005
           }]}

    return query, resp


def test_insertion():
    """ Test variantTypes insertion """
    query = base()
    query['start'] = 85182860
    query['end'] = 85182861
    query['variantType'] = 'INS'
    query['referenceBases'] = 'G'
    del query['alternateBases']
    resp = {"datasetAlleleResponses":
             [{"datasetId": "GRCh37p13:SweGen:20180409",
               "referenceName": "1",
               "callCount": 2000,
               "variantCount": 1,
               "sampleCount": 1000,
               "exists": True,
               "referenceBases": "G",
               "alternateBases": "GT",
               "variantType": "INS",
               "frequeryuency": 0.0005
            }]}
    return query, resp


def test_snp():
    """ Test variantTypes snp """
    query = base()
    query['start'] = 85177156
    query['end'] = 85177157
    query['variantType'] = 'SNP'
    query['referenceBases'] = 'T'
    del query['alternateBases']
    resp = {"datasetAlleleResponses": [
              {"datasetId": "GRCh37p13:SweGen:20180409",
               "referenceName": "1",
               "callCount": 2000,
               "variantCount": 312,
               "sampleCount": 1000,
               "exists": True,
               "referenceBases": "T",
               "alternateBases": "C",
               "variantType": "SNP",
               "frequency": 0.15631263
           }]}
    return query, resp


# TODO
# def test_span():
#     query = base()
#     query['startMin'] = N
#     query['startMax'] = N
#     query['endMin'] = N+M
#     query['endMax'] = N+M
#     return query


tests = [test_deletion, test_insertion, test_snp]
