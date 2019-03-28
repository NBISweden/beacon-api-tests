"""An standard question."""


def base():
    """Return a standard question."""
    # This must be a function so that it always returns a new object
    query = {'referenceName': 22,
             'referenceBases': 'GG',
             'alternateBases': 'N',
             'assemblyId': 'GRCh38',
             'start': 0,
             'end': 2,
             'includeDatasetResponses': 'HIT',
             'datasetIds': 'GRCh38:beacon_test:2030-01-01'
             }
    return query
