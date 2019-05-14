"""Responsible for comparing the responses to the given gold standard."""
import logging
import config.config
import utils.errors as err


# Define what keys that should be used to sort lists of dictionaries
SORT_BY = {'datasets': ['id'], 'datasetAlleleResponses': ['datasetId', 'frequency', 'referenceBases']}


def run_test():
    """Decorator for test queries.

    Run the decorated function and catch and log its errors.
    """
    def decorator(func):
        logging.info('Testing %s\n\t%s', func.__name__, func.__doc__.strip())
        try:
            func()
        except err.ResponseError as r_error:
            # errors from the comparisons of a response, contains a list of errors to report
            logging.error('Test "%s" did not pass: """%s"""', func.__name__, func.__doc__.strip())
            for err_msg in r_error.messages:
                logging.error(err_msg)
        except AssertionError as a_error:
            # other errors
            logging.error('Test "%s" did not pass: """%s"""', func.__name__, func.__doc__.strip())
            logging.error(str(a_error))
        logging.info('Done\n')
    return decorator


def assert_partly_in(gold, response, key):
    """Compare two objects to see that everything in the gold object is also in the other."""
    #  find best match
    #  collect all diffs for this match
    assert key in response, f'Bad response, could not find {key} in {response}'
    assert response[key], f'Too few elements, could not find {gold}'
    comparable = find_best_match_x(gold, response, key)
    errors = []
    compare_obj(gold, comparable, errors=errors)
    if errors:
        raise err.ResponseError(errors)


def assert_not_in(exclude, response, key):
    """Recurse through the object of forbidden values to verify that they are not present."""
    errors = []
    for obj in response[key]:
        not_in(obj, exclude, errors)
    if errors:
        raise err.ResponseError(errors)


def find_best_match_x(gold, resp, key):
    """Compare to objects by a given set of identifiers. Return the number of mismatches."""
    def find_best_match(alist):
        """Sort by fst (identifier), return snd (an object)."""
        if not alist:
            return {}
        return sorted(alist, key=lambda x: x[0])[0][1]

    def get_sort_ids(obj):
        """Sort by normalized key."""
        sorters = SORT_BY.get(key)
        return [normalize(obj.get(sorter)) for sorter in sorters]

    def compare_identifiers(gold, cmp):
        """Compare to objects by a given set of identifiers. Return the number of mismatches."""
        gold_id = get_sort_ids(gold)
        cmp_id = get_sort_ids(cmp)
        if gold_id == cmp_id:
            return 0
        return len([1 for (g, c) in zip(gold_id, cmp_id) if g != c])

    return find_best_match([(compare_identifiers(gold, obj), obj) for obj in resp[key]])


def compare_obj(gold, obj, errors):
    """Help function to compare(), compares objects."""
    for key, val in gold.items():
        if key not in obj:
            errors.append(f'Value missing: {key}  {obj.keys()}')

        elif normalize(val) != normalize(obj[key]):
            errors.append(f'Bad value for field {key}: {val} != {obj[key]}')


def normalize(val):
    """Normalize a value before comparison to other values."""
    if isinstance(val, float):
        return round(val, config.config.PRECISION)
    return val


def not_in(obj, exclude, errors):
    """Verify that forbidden values are not present in the object."""
    for key in exclude.keys():
        if key not in obj:
            # key is not in obj -> ok
            continue

        elif not exclude[key]:
            # empty value in `exclude` -> the key is not accepted
            errors.append(f'Key {key} not allowed in answer')

        elif obj[key] == exclude[key]:
            # equal values -> not ok
            errors.append(f'Value {{{key}: {obj[key]}}} not allowed in answer')
