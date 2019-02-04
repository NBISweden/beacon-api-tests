""" An example question """

def base():
    """ Standard question """
    # This must be a function so that it always returns a new object
    q = {'referenceName': 1,
         'referenceBases': 'GG',
         'alternateBases': 'N',
         'assemblyId': 'GRCh37',
         'start': 0,
         'end': 2,
         'includeDatasetResponses': 'HIT'
        }
    return q
