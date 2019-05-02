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


class ConceptScheme(Concept):
    """A group of concepts."""
    def __iter__(self):
        """Don't yield the ConceptScheme itself when iterating."""
        for c in self.children:
            yield from iter(c)


class Measure(Concept):
    """Concept with a unit."""
    units = None


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

    c_each = Concept(id='each', name='[all model values]')
    c_total = Concept(id='total', name='[Global total or average]')

    yield ConceptScheme(id='model', name='Model', children=[c_each])
    yield ConceptScheme(id='scenario', name='Scenario', children=[c_each])
    yield ConceptScheme(id='region', name='Region', children=[c_each, c_total])
    yield ConceptScheme(id='year', name='Year', children=[c_each])


def add_unit(key, measure):
    """Add units to a key."""
    if isinstance(measure.units, str):
        key.values['unit'] = measure.units
    else:
        # Conditional units
        for condition, unit in measure.units.items():
            dim, value = condition.split(' == ')
            if key.values[dim] == value:
                key.values['unit'] = unit
                return


def make_template(verbose=True):
    """Generate a data template.

    Outputs a 'template.csv' containing all keys specified in 'spec.yaml'.
    """
    # Read dimensions
    with open(join(paths['data'], 'dimensions.yaml')) as f:
        dim_cfg = yaml.load(f)

    dims = read_hierarchy(dim_cfg, ConceptScheme)
    dims.extend(common_dim_dummies())

    # Reorganize as a dict
    dims = {cs.id: cs for cs in dims}

    if verbose:
        print(dims)
        print(list(dims['mode']))

    # Read measures
    with open(join(paths['data'], 'measures.yaml')) as f:
        measure_cfg = yaml.load(f)

    measures = read_hierarchy(measure_cfg, Measure)

    # Reorganize as a dict
    measures = {m.id: m for m in measures}

    # Read specification of the template

    with open(join(paths['data'], 'spec.yaml')) as f:
        spec = yaml.load(f)

    # Process specifications
    common_dims = ['model', 'scenario', 'region', 'year']
    keys = []
    filters = []

    for spec_item in spec:
        # List of dimensions for this Key
        key_dims = common_dims.copy()
        key_dims.extend(spec_item.pop('dims', []))

        # Retrieve the measure to add to the key later
        measure = measures[spec_item.pop('measure')]

        # Iterate, adding keys by Cartesian product over the dimensions
        iters = [iter(dims[d]) for d in key_dims]
        for values in product(*iters):
            kv = dict(zip(key_dims, map(lambda c: c.id, values)))
            kv['measure'] = measure.id
            k = Key(**kv)

            # Add the units
            add_unit(k, measure)

            # Store the key
            keys.append(k)

        # Store any filters with this spec
        for exclude in spec_item.pop('exclude', []):
            filters.append(f"measure == '{measure.id}' and {exclude}")

    # Intermediate output
    spec = pd.DataFrame([k.values for k in keys]).fillna('')

    print('{} rows'.format(spec.shape[0]))

    # Filter rows
    spec = spec.query('not ((' + ') or ('.join(filters) + '))')

    print('{} rows'.format(spec.shape[0]))

    # Convert to an approximation of the traditional iTEM format

    # Helper methods to collapse columns
    def collapse_lca_scope(row):
        lca_scope = row.pop('lca_scope')
        if len(lca_scope):
           row['measure'] += ' (' + lca_scope + ')'
        return row

    def collapse_ghg(row):
        ghg = row.pop('ghg')
        if len(ghg):
           row['measure'] = ghg + ' ' + row['measure']
        return row

    target_cols = common_dims[:-1] + ['measure', 'unit', 'mode', 'technology',
                                      'fuel', 'year']
    rename = {'columns': {'measure': 'variable'}}

    spec = spec.apply(collapse_lca_scope, axis=1) \
               .apply(collapse_ghg, axis=1) \
               .reindex(columns=target_cols) \
               .sort_values(by=['measure', 'mode']) \
               .rename(**rename)

    print(spec)

    spec.to_csv('template.csv')
