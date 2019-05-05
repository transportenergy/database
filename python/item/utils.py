from functools import lru_cache
from itertools import product
from os.path import join

from item.common import paths
import pandas as pd
import yaml


# Class definitions

class Nameable:
    """Base class."""
    id = None
    name = None
    description = None

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __repr__(self):
        return '<{0}: {1.id}, {1.name} ({2})>'.format(
                self.__class__.__name__, self,
                len(self))


class Concept(Nameable):
    children = []

    def __len__(self):
        """Size of the Concept is the count of itself + any children."""
        return len(self.children) + sum(map(len, self.children))

    def __iter__(self):
        """Iterate over the Concept itself, then any children."""
        yield self
        for c in self.children:
            yield from iter(c)

    @lru_cache()
    def get_child(self, id):
        for obj in iter(self):
            if obj.id == id:
                return obj
        raise ValueError(id)


class ConceptScheme(Concept):
    """A group of concepts."""
    def __iter__(self):
        """Don't yield the ConceptScheme itself when iterating."""
        for c in self.children:
            yield from iter(c)


class Measure(Concept):
    """Concept with a unit."""
    unit = None


class Key:
    """Key for an observation."""
    # Values of the *key* (NOT the observation itself) as a map: dim → value
    values = {}

    def __init__(self, **kwargs):
        self.values = kwargs


def read_hierarchy(root, klass=Concept):
    """Recursively read Concept and subclasses."""
    result = []

    # Iterate over keys and children
    for c_id, contents in root.items():
        if contents is None:
            # No children, _name, _description, etc.
            contents = {}
        elif c_id.startswith('_'):
            # This child is an attribute value like _name
            continue

        # Create an object
        c = klass(id=c_id)

        # Store the _name, _description, etc.
        for k, v in contents.items():
            if k.startswith('_'):
                 setattr(c, k.lstrip('_'), v)

        # Default name:
        if c.name is None:
            c.name = c.id.title()

        # Recurse
        c.children = read_hierarchy(contents)

        # Append to the result
        result.append(c)

    return result


def common_dim_dummies():
    """Yield dummy ConceptSchemes for the common dimensions."""

    c_all = Concept(id='[All]', name='[all model values]')
    c_total = Concept(id='[All + World]', name='[Global total or average]')

    yield ConceptScheme(id='model', name='Model', children=[c_all])
    yield ConceptScheme(id='scenario', name='Scenario', children=[c_all])
    yield ConceptScheme(id='region', name='Region', children=[c_total])
    yield ConceptScheme(id='year', name='Year', children=[c_all])


def add_unit(key, measure):
    """Add units to a key."""
    if isinstance(measure.unit, str):
        key.values['unit'] = measure.unit
    else:
        # Conditional units
        for condition, unit in measure.unit.items():
            dim, value = condition.split(' == ')
            if key.values[dim] == value:
                key.values['unit'] = unit
                return


def read_concepts(path):
    """Read dimensions from file."""
    with open(path) as f:
        concepts = read_hierarchy(yaml.load(f), ConceptScheme)

    # Add common dimensions
    concepts.extend(common_dim_dummies())

    # Reorganize as a dict
    return {c.id: c for c in concepts}


def read_measures(path):
    """Read measures from file."""
    measures = ConceptScheme(id='measure')

    with open(path) as f:
        measures.children = read_hierarchy(yaml.load(f), Measure)

    return measures


def make_template(verbose=True):
    """Generate a data template.

    Outputs a 'template.csv' containing all keys specified in 'spec.yaml'.
    """

    # Concepts (used as dimensions) and possible values
    dims = read_concepts(join(paths['data'], 'concepts.yaml'))

    # Measures and units
    dims['measure'] = read_measures(join(paths['data'], 'measures.yaml'))

    # Common dimensions applied to all keys
    common_dims = ['model', 'scenario', 'region', 'year']

    # List of Key objects representing data to appear in the template
    keys = []

    # Read specification of the template
    with open(join(paths['data'], 'spec.yaml')) as f:
        specs = yaml.load(f)

    # Filters to reduce the set of keys; see below at 'Filter keys'
    filters = []

    # Process specifications
    for spec in specs:
        try:
            # Retrieve the measure to add to the key later
            measure = dims['measure'].get_child(spec.pop('measure'))

            # Store any filters with this spec
            for exclude in spec.pop('exclude', []):
                filters.append(f"measure == '{measure.id}' and {exclude}")
        except KeyError:
            # Entry without a 'measure:' key = a list of general exclusions
            filters.extend(spec.pop('exclude'))
            continue

        # List of dimensions for this Key
        key_dims = common_dims + spec.pop('dims', [])

        # A list of iterable objects containing the values along each dimension
        iters = [iter(dims[d]) for d in key_dims]

        # Iterate, adding keys by Cartesian product over the dimensions
        for values in product(*iters):
            # Create a Key with these values and the measure
            kv = dict(zip(key_dims, map(lambda c: c.id, values)))
            kv['measure'] = measure.id
            k = Key(**kv)

            # Add the units
            add_unit(k, measure)

            # Store the key
            keys.append(k)

    # Convert list → DataFrame
    specs = pd.DataFrame([k.values for k in keys]).fillna('')

    if verbose:
        print('{} rows'.format(specs.shape[0]), end='\n\n')

    # Filter rows
    for filter in filters:
        if verbose:
            query_str = '~ ( {} )'.format(filter)
            print('Filtering: {}'.format(query_str))

        specs.query(query_str, inplace=True)

        if verbose:
            print('  … {} rows'.format(specs.shape[0]))

    # Convert to an approximation of the traditional iTEM format

    # Use names instead of IDs for these columns
    use_name_cols = ['type', 'mode', 'vehicle', 'technology', 'fuel', 'ghg',
                     'measure']

    # Order of output columns
    target_cols = common_dims[:-1] + ['measure', 'unit', 'mode', 'technology',
                                      'fuel', 'year']

    # Columns to sort content
    sort_cols = ['measure', 'unit', 'type', 'mode', 'vehicle', 'technology',
                 'fuel', 'lca_scope', 'ghg']

    # Helper methods
    def use_names(row):
        """Use names instead of IDs for some columns."""
        for col in use_name_cols:
            if len(row[col]):
                name = dims[col].get_child(row[col]).name
                if name == 'All' and col in ['technology']:
                    name = 'Total'
                row[col] = name
        return row

    def collapse(row):
        """Collapse multiple concepts into fewer columns."""
        lca_scope = row.pop('lca_scope')
        if len(lca_scope):
           row['measure'] += ' (' + lca_scope + ')'

        ghg = row.pop('ghg')
        if len(ghg):
           row['measure'] = ghg + ' ' + row['measure']

        type = row.pop('type')
        if len(type):
            if row['mode'] in ['Road', 'Rail']:
                row['mode'] = type + ' ' + row['mode']
            elif row['mode'] == 'All':
                row['mode'] = row['mode'] + ' ' + type

        vehicle = row.pop('vehicle')
        if len(vehicle) and vehicle != 'All':
            row['mode'] = vehicle

        return row

    # Perform several operations efficiently by chaining
    # - Replace some IDs with names
    # - Sort
    specs = specs.apply(use_names, axis=1) \
                 .sort_values(by=sort_cols) \
                 .apply(collapse, axis=1) \
                 .reindex(columns=target_cols) \
                 .reset_index(drop=True) \
                 .rename(columns={'measure': 'variable'}) \
                 .rename(columns=lambda name: name.title())

    if verbose:
        print('\n', specs.head(10))

    # Save in multiple formats
    specs.to_csv('template.csv', index=False)
    specs.to_excel('template.xlsx', index=False)
