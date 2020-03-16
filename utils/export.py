import logging
import tempfile
from pathlib import Path
import yaml
import config.config
import utils.jsonschemas


def export_csv_testdata(filepaths):
    """Export data in csv from a list of test file paths."""
    sep = get_separator('csv')
    schema_path = config.config.TEST_SPEC
    schema = yaml.load(open(schema_path), Loader=yaml.SafeLoader)
    #metadata_headers = schema['definitions']['query_metadata']['properties']\
    #                         ['datasets']['items']['properties']['dataset']\
    #                         ['properties'].keys()
    variants_headers = schema['definitions']['datafields'].keys()

    metadata = variants_headers
    metadata, variants = [], []
    for testfile in filepaths:
        testyaml = utils.jsonschemas.load_and_validate_test(testfile)
        variant = extract_data(testyaml, variants_headers, sep)
        variants += variant

    meta_header = [f"# {sep.join(metadata_headers)}"]
    variant_header = [f"# {sep.join(variants_headers)}"]
    output = '\n'.join(meta_header + list(set(metadata)) + variant_header + list(set(variants)))
    return output


def export_vcf_testdata(filepaths):
    """Extract all vcf lines that a test refers to."""
    refs = get_vcf_references(filepaths)
    data = []
    for filep, ids in refs.items():
        metadata, info = get_vcf_data(filep, ids)
        if info:
            data.append((filep, metadata, info))
    return data


def extract_data(testyaml, variants_headers, sep):
    """Extract the data (for the beacon's database) from a test file."""
    variants = []
    for test in testyaml:
        if 'beacondata' in test:
            variants.extend(extract_variants(test['beacondata'], variants_headers, sep))
    return variants


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


def get_vcf_data(filep, ids):
    """Extract relevant lines from a vcf."""
    path = Path(filep)
    metadata, info = [], []
    matched_id = set()
    if not path.exists():
        path = 'testdata' / Path(filep)
        if not path.exists():
            logging.warning(f'vcf file {path} not found')
            return metadata, info
    for line in open(path):
        if line.startswith('#'):
            metadata.append(line)
            continue
        matched_id.update(vcf_match_id(line, ids))
        if '*' in ids or matched_id:
            info.append(line)
    if len(matched_id) < len(ids):
        logging.warning(f'No vcf matches for id {", ".join(ids.difference(matched_id))}')
    return metadata, info


def get_vcf_references(filepaths):
    """Get all references to vcf data. Return a dict with filepath and ids."""
    refs = {}
    for testfile in filepaths:
        testyaml = utils.jsonschemas.load_and_validate_test(testfile)
        for test in testyaml:
            if 'vcf' in test:
                filep, ref = test['vcf'].split(':', 1)
                if filep not in refs:
                    refs[filep] = set()
                refs[filep].update(ref.split(','))
    return refs


def print_vcf_files(data, print_metadata):
    """Print data to a vcf file."""
    for name, metadata, info in data:
        fh = tempfile.NamedTemporaryFile(dir='.', prefix='testdata_', suffix='.vcf', delete=False)
        logging.info(f'>> Writing from {name} to {Path(fh.name).name}.')
        for line in metadata:
            if not line.startswith('##') or print_metadata:
                fh.file.write(line.encode())
        fh.file.write(''.join(info).encode())
        fh.close()


def vcf_match_id(line, ids):
    """Check whether the ids on a vcf line matches any of the given ones."""
    try:
        lineids = line.split('\t')[2].split(',')
    except IndexError:
        logging.warning(f'Could not find id in vcf line {line}')
    return ids.intersection(lineids)


def show_data_files(testfiles):
    """Print all names of all test data files used by the given tests."""
    datafiles = set()
    for testfile in testfiles:
        testdir = Path(testfile).parent
        testyaml = utils.jsonschemas.load_and_validate_test(testfile)
        for test in testyaml:
            if 'beacondata' in test:
                datafiles.add(str(testdir / test['beacondata']))
    print('\n'.join(datafiles))
