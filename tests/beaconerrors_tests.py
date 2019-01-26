"""
Queries that are not allowed, but cannot be formally forbidden by openapi
(eg dependencies and mutual exclusivness).
Check that the beacon does not allow these
"""
from .basequery import base


def no_alternate():
    """ Check that either alternateBases or variantType is required """
    # should complain about not finding variantType
    query = base()
    del query['alternateBases']
    return query, {}


tests = [no_alternate]


## TO BE REMOVED?
# Finnish be sets all excluded start/stop-parameters to 0
# Start and end positions default to 0, so these tests are no good
#
# def start1():
#     # end defaultar till 0
#     # - start only. is variantType allowed here?
#     #   "the size is given through the specified alternateBases"
#     #   "the use of start without an end parameter requires the use of referenceBases" (hmm, referenceBases always required)
#     q = base()
#     del q['end']
#     return q, {}
# 
# 
# def start2():
#     # startMin, startMax, endMax defaultar till 0
#     q = base()
#     del q['end']
#     q['endMin'] = '2'
#     return q, {}
# 
# 
# def start_nostart():
#     q = base()
#     del q['start']
#     del q['end']
#     q['endMin'] = '2'
#     q['endMax'] = '2'
#     return q, {}
# 
# 
# def start_noend():
#     q = base()
#     del q['start']
#     del q['end']
#     q['startMin'] = '2'
#     q['startMax'] = '2'
#     return q, {}
# 
# 
# def start_nomin():
#     q = base()
#     del q['start']
#     del q['end']
#     q['startMin'] = '2'
#     q['endMin'] = '2'
#     q['endMax'] = '2'
#     return q, {}
