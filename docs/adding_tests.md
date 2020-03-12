# Writing tests

An example test looks like this

```
- name: test_snp
  descr:
    Test variantType SNP.
  query:
    includeDatasetResponses: HIT
    datasetIds:
      - beacon_testdataset
    assemblyId: GRCh38
    referenceName: "22"
    start: 17302971
    variantType: SNP
    referenceBases: C
  results:
    - property: datasetAlleleResponses
      assert: contains
      data:
        datasetId: beacon_testdataset
        exists: true
  beacondata: testdata.csv
 ```

This test verifies that the variant `22 : 17302971 A > C` is present in dataset `beacon_testdataset`,
i.e. that the beacon's answer to the given query should contain `{exists: true, datasetId: beacon_testdataset}`
in the field `datasetAlleleResponses`.

The field `beacondata` refers to a file `testdata.vcf`, which contains all data that should be loaded to the Beacon in order
for this test to pass. This file might look like this:

```
# referenceName,referenceBases,alternateBases,variantType,assemblyId,start,end,mateName,datasetId
22,C,A,SNP,GRCh38,17302971,17302972,None,GRCh38:beacon_test:2030-01-01
22,A,G,None,GRCh38,17300407,17300408,None,GRCh38:beacon_test:2030-01-01
22,A,G,SNP,GRCh38,16050074,16050075,None,GRCh38:beacon_test:2030-01-01
22,TG,None,SNP,GRCh38,16577043,16577045,None,GRCh38:beacon_test:2030-01-01
22,TG,AG,SNP,GRCh38,16577043,None,None,GRCh38:beacon_test:2030-01-01
22,TG,AG,SNP,GRCh38,16577043,None,None,GRCh38:beacon_test2:2030-01-01
```

For a more detailed description of the tests, see the [markdown schema](schema.md) or
the [yaml schema](../tests/schema.yaml).

You can validate the structure of your test by running:
`python3 beacon_api_tester.py --validate_tests tests/my_new_test.yaml`
