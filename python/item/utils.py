from functools import lru_cache
from itertools import product
from os.path import join

from item.common import paths
import pandas as pd
from pandas.core.computation.ops import UndefinedVariableError
import yaml


# Class definitions
#
# These are based on the SDMX information model; SDMX is not used directly,
# because there is currently no mature Python package for it.

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
    """A Concept with a unit."""
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
    """Yield dummy ConceptSchemes for the common dimensions.

    Each of these has only 1 item. Submitted datasets will have multiple values
    along each of these dimensions.
    """

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
            if dim in key.values and key.values[dim] == value:
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

    Outputs files containing all keys specified in 'spec.yaml'. The file is
    produced in two formats:

    - template.csv
    - template.xlsx

    .. todo:: Allow filtering on concepts that are parents of other concepts.
    """

    # Concepts (used as dimensions) and possible values
    dims = read_concepts(join(paths['data'], 'concepts.yaml'))

    # Measures and units
    dims['measure'] = read_measures(join(paths['data'], 'measures.yaml'))

    # Common dimensions applied to all keys
    common_dims = ['model', 'scenario', 'region', 'year']

    # Read specification of the template
    with open(join(paths['data'], 'spec.yaml')) as f:
        specs = yaml.load(f)

    # Filters to reduce the set of Keys; see below at 'Filter Keys'
    exclude_global = []

    # Processed dataframes
    dfs = []

    # Process each entry in the spec file
    for n_spec, spec in enumerate(specs):
        # List of Key objects representing data
        keys = []

        try:
            # Retrieve the measure to add to the key later
            measure = dims['measure'].get_child(spec.pop('measure'))
        except KeyError:
            # Entry without a 'measure:' key is a list of global filters
            exclude_global = spec.pop('exclude')
            continue

        # List of dimensions for these Keys
        key_dims = common_dims + spec.pop('dims', [])

        # A list of iterable objects containing the values along each dimension
        iters = [iter(dims[d]) for d in key_dims]

        # Iterate, adding keys by Cartesian product over the dimensions
        for values in product(*iters):
            # Create a Key with these values, the sort order, and the measure
            kv = dict(zip(key_dims, map(lambda c: c.id, values)),
                      sort_order=n_spec, measure=measure.id)
            k = Key(**kv)

            # Add appropriate units
            add_unit(k, measure)

            # Store the Key
            keys.append(k)

        if verbose:
            print("\nSpec for '{}': {} keys".format(measure.id, len(keys)))

        # Convert list → DataFrame for filtering
        df = pd.DataFrame([k.values for k in keys]).fillna('')

        # Filter Keys by both global and spec-specific filters
        for filter in exclude_global + spec.pop('exclude', []):
            # 'not' operator (~) to exclude the matching rows
            query_str = '~({})'.format(filter)

            try:
                df.query(query_str, inplace=True)
            except UndefinedVariableError:
                # Filter references a dimension that's not in this dataframe;
                # the filter isn't relevant
                continue

            if verbose:
                print('  {} keys after filtering {}'.format(df.shape[0],
                                                            query_str))

        # Store the filtered keys as a dataframe
        dfs.append(df)

    # Combine all dataframes
    specs = pd.concat(dfs, axis=0, sort=False) \
              .fillna('')

    # Convert to an approximation of the traditional iTEM format

    # Use names instead of IDs for these columns
    use_name_cols = ['type', 'mode', 'vehicle', 'technology', 'fuel',
                     'pollutant', 'automation', 'operator', 'measure']

    # Order of output columns
    target_cols = common_dims[:-1] + ['measure', 'unit', 'mode', 'technology',
                                      'fuel', 'year']

    # Columns to sort content
    sort_cols = ['sort_order', 'measure', 'unit', 'type', 'mode', 'vehicle',
                 'technology', 'fuel', 'lca_scope', 'pollutant']

    # Helper methods
    def use_names(row):
        """Use names instead of IDs for some columns."""
        for col in use_name_cols:
            if len(row[col]):
                name = dims[col].get_child(row[col]).name

                # Where 'All' appears in the technology column, the template
                # requests totals.
                if name == 'All' and col in ['technology']:
                    name = 'Total'
                row[col] = name
        return row

    def collapse(row):
        """Collapse multiple concepts into fewer columns."""
        # Combine 3 concepts with 'measure' ("Variable")
        lca_scope = row.pop('lca_scope')
        if len(lca_scope):
           row['measure'] += ' (' + lca_scope + ')'

        pollutant = row.pop('pollutant')
        if len(pollutant):
           row['measure'] = pollutant + ' ' + row['measure']

        fleet = row.pop('fleet')
        if len(fleet):
            if row['measure'] == 'Energy intensity' and fleet == 'all':
                fleet = ''
            else:
                fleet = ' (' + fleet + ' vehicles)'
            row['measure'] += fleet

        # Combine 4 concepts with 'mode'
        type = row.pop('type')
        if len(type):
            if row['mode'] in ['Road', 'Rail']:
                row['mode'] = type + ' ' + row['mode']
            elif row['mode'] == 'All':
                row['mode'] = row['mode'] + ' ' + type

        vehicle = row.pop('vehicle')
        if len(vehicle) and vehicle != 'All':
            row['mode'] = vehicle

        operator = row.pop('operator')
        automation = row.pop('automation')
        if len(operator) and len(automation) and row['mode'] == 'LDV':
            automation = '' if automation == 'Human' else ' AV'
            row['mode'] += ' ({}{})'.format(operator.lower(), automation)

        return row

    # Chain several operations for better performance
    # - Replace some IDs with names
    # - Sort
    # - Collapse multiple columns into fewer
    # - Set preferred column order
    # - Drop the integer index
    # - Rename columns to Title Case
    specs = specs.apply(use_names, axis=1) \
                 .sort_values(by=sort_cols) \
                 .apply(collapse, axis=1) \
                 .reindex(columns=target_cols) \
                 .reset_index(drop=True) \
                 .rename(columns={'measure': 'variable'}) \
                 .rename(columns=lambda name: name.title())

    if verbose:
        print('', 'Total keys: {0[0]}'.format(specs.shape), specs.head(10),
              sep='\n\n')

    # Save in multiple formats
    specs.to_csv('template.csv', index=False)
    specs.to_excel('template.xlsx', index=False)
