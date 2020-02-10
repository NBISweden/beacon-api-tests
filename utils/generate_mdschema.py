"""Generate markdown information about tests from the test schema."""
import sys
import yaml
try:
    import config.config
except ModuleNotFoundError:
    pass


def generate(schema):
    """TODO."""
    print('# Defining tests')
    try:
        schema = schema or config.config.TEST_SPEC
    except:
        print('Could not find test schema', sys.stderr)
        exit(1)
    with open(schema) as fileh:
        jschema = yaml.load(fileh, Loader=yaml.SafeLoader)
    generate_main(jschema)
    generate_query(jschema)
    generate_result(jschema)


def generate_main(schema):
    info = {'standard': {}, 'optional': {}, 'advanced': {}}
    for key, val in schema['items']['properties'].items():
        info_type = val.get('value')
        if info_type in info:
            info[info_type][key] = val.get('title', '')
            if '$ref' in val and info_type == 'standard':
                info[info_type][key] += ' See below.'
            if 'example' in val:
                ex = 'Example:\n```\n' + val["example"].replace('\\n', '\n') + '\n```'
                info[info_type][key] += f'\n{ex}'
    for level, items in info.items():
        print(f'### {level.title()}')
        for key, val in items.items():
            print(f'- `{key}`: {val}')
            print('')
    print('\n')


def generate_query(schema):
    print('## Query\n')
    query = schema['definitions']['query']
    print(query.get('title'))
    print('')
    print('| Name | Type  |')
    print('| ---- | ----  |')
    for key, val in query['properties'].items():
        if isinstance(val['type'], list):
            types = ', '.join(val['type'])
        else:
            types = val['type']
        print(f'| {key} | {types} |')
    print('\n\n')


def generate_result(schema):
    print('## Comparisons')
    for choice in schema['definitions']['results']['items']['allOf'][0]['oneOf']:
        ac = ' | '.join([f'`{c}`' for c in choice['properties']['assert'].get('enum')])
        print(f'- `assert`: {ac}')
        print('')
        for field in choice['required']:
            fdata = schema['definitions']['results']['items']['properties'].get(field, {})
            ftype = fdata.get('type', '')
            descr = fdata.get('title', '')
            fieldtype = f"<{ftype}>" if ftype else ""
            print(f'  `{field}`: {fieldtype} {descr}')
            print('')
    print('\n\n')


if __name__ == "__main__":
    generate(sys.argv[1])
