"""Responsible for comparing the responses to the given gold standard."""
import config.config
import utils.errors as err


# Define what keys that should be used to sort lists of dictionaries
SORT_BY = {
    'datasets': ['id'],
    'datasetAlleleResponses': ['datasetId', 'frequency', 'referenceBases']
}


def assert_partly_in(gold, response, key):
    """Compare two objects to see that everything in the gold object is also in the other."""
    #  find best match
    #  collect all diffs for this match
    assert key in response, f'Bad response, could not find {key} in {response}'
    assert response[key], f'Too few elements, could not find {gold}'
    comparable = find_matching_object(gold, response, key)
    errors = compare_obj(gold, comparable)
    if errors:
        raise err.ResponseError(errors)


def assert_not_in(exclude, response, key):
    """Recurse through the object of forbidden values to verify that they are not present."""
    errors = []
    # Gather up all errors from all objects before failing
    for obj in response[key]:
        errors.extend(not_in(obj, exclude))
    if errors:
        raise err.ResponseError(errors)


def find_matching_object(gold, resp, key):
    """Compare to objects by a given set of identifiers. Return the number of mismatches."""
    def find_best_match(alist):
        """Sort by fst (identifier), return snd (an object)."""
        if not alist:
            return {}
        return sorted(alist, key=lambda x: x[0])[0][1]

    def get_sort_ids(obj):
        """Sort by normalized key."""
        if key in SORT_BY:
            sorters = SORT_BY.get(key)
        else:
            sorters = obj.keys()
        return [normalize(obj.get(sorter)) for sorter in sorters]

    def compare_identifiers(gold, cmp):
        """Compare to objects by a given set of identifiers. Return the number of mismatches."""
        gold_id = get_sort_ids(gold)
        cmp_id = get_sort_ids(cmp)
        if gold_id == cmp_id:
            return 0
        return len([1 for (g, c) in zip(gold_id, cmp_id) if g != c])

    return find_best_match([(compare_identifiers(gold, obj), obj) for obj in resp[key]])


def compare_obj(gold, obj):
    """Help function to compare(), compares objects."""
    errors = []
    for key, val in gold.items():
        if key not in obj:
            errors.append(f'Value missing: {key}  {obj.keys()}')

        elif normalize(val) != normalize(obj[key]):
            errors.append(f'Bad value for field {key}: {val} != {obj[key]}')
    return errors


def normalize(val):
    """Normalize a value before comparison to other values."""
    if isinstance(val, float):
        return round(val, config.config.PRECISION)
    return val


def not_in(obj, exclude):
    """Verify that forbidden values are not present in the object."""
    errors = []
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
    return errors
