import yaml
import utils.jsonschemas


def export_csv_testdata(filepaths):
    """Export data in csv from a list of test file paths."""
    sep = get_separator('csv')
    schema_path = 'tests/schema.yaml'  # TODO don't hardcode path
    schema = yaml.load(open(schema_path), Loader=yaml.SafeLoader)
    metadata_headers = schema['definitions']['beacondata']['properties']\
                             ['datasets']['items']['properties']['dataset']\
                             ['properties'].keys()
    variants_headers = schema['definitions']['beacondata']['properties']\
                             ['variants']['items']['properties']\
                             ['variant'].keys()

    metadata, variants = [], []
    for testfile in filepaths:
        testyaml = utils.jsonschemas.load_and_validate_test(testfile)
        meta, variant = extract_data(testyaml, metadata_headers, variants_headers, sep)
        metadata += meta
        variants += variant

    meta_header = [f"# {sep.join(metadata_headers)}"]
    variant_header = [f"# {sep.join(variants_headers)}"]
    output = '\n'.join(meta_header + list(set(metadata)) + variant_header + list(set(variants)))
    return output


def extract_data(testyaml, metadata_headers, variants_headers, sep):
    """Extract the data (for the beacon's database) from a test file."""
    metadata, variants = [], []
    for test in testyaml:
        if 'beacondata' in test:
            metadata.extend(extract_metadata(test['beacondata'], metadata_headers, sep))
            variants.extend(extract_variants(test['beacondata'], variants_headers, sep))
    return metadata, variants


def extract_metadata(beacondata, headers, separator):
    """Extract the dataset metadata from the test file."""
    meta = []
    for dataset in beacondata.get('datasets', []):
        data, output = dataset['dataset'], []
        for header in headers:
            output.append(str(data.get(header)))
        meta.append(separator.join(output))
    return meta


def extract_variants(beacondata, headers, separator):
    """Extract the variants from the test file."""
    meta = []
    for dataset in beacondata.get('variants', []):
        data, output = dataset['variant'], []
        for header in headers:
            output.append(str(data.get(header)))
        meta.append(separator.join(output))
    return meta


def get_separator(out_format):
    """
    Define how elements should be separated.

    To be improved, now only supports csv or tsv.
    """
    if out_format == 'csv':
        return ','
    return '\t'
