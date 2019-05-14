"""Example tests. Check that they work and that we get the expected output."""

from tests.basequery import base
from utils.beacon_query import call_beacon
from utils.validate import assert_partly_in, run_test


@run_test()
def test_info():
    """Test the beacon's info (/) call."""
    resp = call_beacon(path='/')  # takes care of calling, validating to schemas, status code
    counts = {"id": "GRCh38:beacon_test:2030-01-01",
              "assemblyId": "GRCh38",
              "variantCount": 17,
              "callCount": 12,
              "sampleCount": 2504
              }
    assert_partly_in(counts, resp, 'datasets')


@run_test()
def test_search_1():
    """Test a standard query with alternateBases, start and end."""
    query = base()
    query['start'] = 16050074
    query['end'] = 16050075
    query['referenceBases'] = 'A'
    query['alternateBases'] = 'G'
    gold = {"datasetId": "GRCh38:beacon_test:2030-01-01",
            "referenceName": "22",
            "callCount": 5008,
            "variantCount": 1,
            "sampleCount": 2504,
            "exists": True,
            "referenceBases": "A",
            "alternateBases": "G",
            "variantType": "SNP",
            "frequency": 0.000199681
            }
    resp = call_beacon(query=query)
    assert_partly_in(gold, resp, 'datasetAlleleResponses')


@run_test()
def test_snp():
    """Test variantType SNP."""
    query = base()
    query['start'] = 17302971
    query['end'] = 17302972
    query['variantType'] = 'SNP'
    query['referenceBases'] = 'C'
    del query['alternateBases']
    resp = call_beacon(query=query)
    gold = {"datasetId": "GRCh38:beacon_test:2030-01-01",
            "referenceName": "22",
            "callCount": 5008,
            "variantCount": 2931,
            "sampleCount": 2504,
            "exists": True,
            "referenceBases": "C",
            "alternateBases": "A",
            "variantType": "SNP",
            "frequency": 0.585264
            }
    assert_partly_in(gold, resp, 'datasetAlleleResponses')


@run_test()
def test_bad_end():
    """Test querying with a bad end position."""
    query = base()
    query['start'] = 17300407
    query['end'] = 17300409
    query['referenceBases'] = 'A'
    query['alternateBases'] = 'G'
    resp = call_beacon(query=query)
    assert not resp['exists'], 'Beacon found match for bad query'


@run_test()
def test_end():
    """Test the same query as `test_bad_end()` but with the correct end position."""
    query = base()
    query['start'] = 17300407
    query['end'] = 17300408
    query['referenceBases'] = 'A'
    query['alternateBases'] = 'G'
    resp = call_beacon(query=query)
    gold = {"datasetId": "GRCh38:beacon_test:2030-01-01",
            "referenceName": "22",
            "callCount": 5008,
            "variantCount": 4723,
            "sampleCount": 2504,
            "exists": True,
            "referenceBases": "A",
            "alternateBases": "G",
            "variantType": "SNP",
            "frequency": 0.943091
            }
    assert_partly_in(gold, resp, 'datasetAlleleResponses')


@run_test()
def test_insertion():
    """Test variantTypes INS."""
    query = base()
    query['start'] = 16064512
    query['end'] = 16064513
    query['variantType'] = 'INS'
    query['referenceBases'] = 'A'
    del query['alternateBases']
    resp = call_beacon(query=query)

    gold = {"datasetId": "GRCh38:beacon_test:2030-01-01",
            "referenceName": "22",
            "callCount": 5008,
            "variantCount": 21,
            "sampleCount": 2504,
            "exists": True,
            "referenceBases": "A",
            "alternateBases": "AAGAATGGCCTAATAC",
            "variantType": "INS",
            "frequency": 0.00419329
            }
    assert_partly_in(gold, resp, 'datasetAlleleResponses')


@run_test()
def test_insertion_altbase():
    """Test variantTypes by searching for ref and alt."""
    query = base()
    query['start'] = 16539540
    query['end'] = 16539541
    query['referenceBases'] = 'A'
    query['alternateBases'] = 'AC'
    resp = call_beacon(query=query)
    gold = {"datasetId": "GRCh38:beacon_test:2030-01-01",
            "referenceName": "22",
            "callCount": 5008,
            "variantCount": 7,
            "sampleCount": 2504,
            "exists": True,
            "referenceBases": "A",
            "alternateBases": "AC",
            "variantType": "INS",
            "frequency": 0.00139776
            }
    assert_partly_in(gold, resp, 'datasetAlleleResponses')


@run_test()
def test_multi_insertion():
    """Find a variantTypes INS at a position where there are two different variants."""
    query = base()
    query['start'] = 16879600
    query['end'] = 16879601
    query['referenceBases'] = 'T'
    del query['alternateBases']
    query['variantType'] = 'INS'
    resp = call_beacon(query=query)
    gold = {"datasetId": "GRCh38:beacon_test:2030-01-01",
            "referenceName": "22",
            "callCount": 5008,
            "variantCount": 116,
            "sampleCount": 2504,
            "exists": True,
            "referenceBases": "T",
            "alternateBases": "TAA",
            "variantType": "INS",
            "frequency": 0.023162939,
            }
    gold2 = {"datasetId": "GRCh38:beacon_test:2030-01-01",
             "referenceName": "22",
             "callCount": 5008,
             "variantCount": 314,
             "sampleCount": 2504,
             "exists": True,
             "referenceBases": "T",
             "alternateBases": "TA",
             "variantType": "INS",
             "frequency": 0.062699683,
             }
    assert_partly_in(gold, resp, 'datasetAlleleResponses')
    assert_partly_in(gold2, resp, 'datasetAlleleResponses')


@run_test()
def test_deletion_altbase():
    """Test a deletion by searching for ref and alt."""
    query = base()
    query['start'] = 16497140
    query['end'] = 16497143
    query['referenceBases'] = 'CTT'
    query['alternateBases'] = 'C'
    resp = call_beacon(query=query)
    gold = {"datasetId": "GRCh38:beacon_test:2030-01-01",
            "referenceName": "22",
            "callCount": 5008,
            "variantCount": 4,
            "sampleCount": 2504,
            "exists": True,
            "referenceBases": "CTT",
            "alternateBases": "C",
            "variantType": "DEL",
            "frequency": 0.000798722
            }
    assert_partly_in(gold, resp, 'datasetAlleleResponses')
    return query, resp


@run_test()
def test_deletion():
    """Test variantTypes DEL."""
    query = base()
    query['start'] = 16517679
    query['end'] = 16517684
    query['referenceBases'] = 'GACAA'
    del query['alternateBases']
    query['variantType'] = 'DEL'
    resp = call_beacon(query=query)
    gold = {"datasetId": "GRCh38:beacon_test:2030-01-01",
            "referenceName": "22",
            "callCount": 5008,
            "variantCount": 3,
            "sampleCount": 2504,
            "exists": True,
            "referenceBases": "GACAA",
            "alternateBases": "G",
            "variantType": "DEL",
            "frequency": 0.000599042
            }
    assert_partly_in(gold, resp, 'datasetAlleleResponses')


@run_test()
def test_deletion_2():
    """Test variantTypes DEL with startMin/startMax."""
    query = base()
    del query['start']
    del query['end']
    query['startMin'] = 17301520
    query['startMax'] = 17301530
    query['endMin'] = 17301535
    query['endMax'] = 17301536
    query['referenceBases'] = 'ATACATAGTC'
    del query['alternateBases']
    query['variantType'] = 'DEL'
    resp = call_beacon(query=query)
    gold = {"datasetId": "GRCh38:beacon_test:2030-01-01",
            "referenceName": "22",
            "callCount": 5008,
            "variantCount": 2932,
            "sampleCount": 2504,
            "exists": True,
            "referenceBases": "ATACATAGTC",
            "alternateBases": "A",
            "variantType": "DEL",
            "frequency": 0.585463
            }
    assert_partly_in(gold, resp, 'datasetAlleleResponses')


@run_test()
def test_snp_mnp():
    """Test representation of TG->AG and multiple variations from one vcf line."""
    query = base()
    query['start'] = 16577043
    query['end'] = 16577045
    query['referenceBases'] = 'TG'
    del query['alternateBases']
    query['variantType'] = 'SNP'

    resp = call_beacon(query=query)
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
    assert_partly_in(gold, resp, 'datasetAlleleResponses')


@run_test()
def test_multi():
    """Test alternateBases=N and multiple variations from one vcf line (indel)."""
    query = base()
    query['start'] = 19617926
    query['referenceBases'] = 'N'
    query['alternateBases'] = 'N'
    del query['end']
    resp = call_beacon(query=query)
    golds = [
        {"datasetId": "GRCh38:beacon_test:2030-01-01",
         "referenceName": "22",
         "callCount": 5008,
         "variantCount": 17,
         "sampleCount": 2504,
         "exists": True,
         "referenceBases": "GTCT",
         "alternateBases": "GTCTTCTTCT",
         "variantType": "INS",
         "frequency": 0.00339457
         },
        {"datasetId": "GRCh38:beacon_test:2030-01-01",
         "referenceName": "22",
         "callCount": 5008,
         "variantCount": 118,
         "sampleCount": 2504,
         "exists": True,
         "referenceBases": "GTCT",
         "alternateBases": "GTCTTCT",
         "variantType": "INS",
         "frequency": 0.0235623
         },
        {"datasetId": "GRCh38:beacon_test:2030-01-01",
         "referenceName": "22",
         "variantCount": 182,
         "callCount": 5008,
         "sampleCount": 2504,
         "exists": True,
         "referenceBases": "GTCT",
         "alternateBases": "G",
         "variantType": "DEL",
         "frequency": 0.036341853
         }]
    for gold in golds:
        assert_partly_in(gold, resp, 'datasetAlleleResponses')
