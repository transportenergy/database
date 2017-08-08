from functools import reduce
from itertools import chain
import operator
from os.path import join

from plotnine import ggplot, aes, labs, scale_linetype

from item.common import paths
from item.model import select
from item.model.common import INDEX
from item.model.dimensions import INFO


scale_linetype_scenario = scale_linetype(limits=['reference',
                                                 'policy'])


def min_max(data, dims):
    """Add 'min' and 'max' columns to *data*, grouped on *dims*."""
    grp = data.groupby(dims)['value']
    data['min'] = grp.transform('min')
    data['max'] = grp.transform('max')
    data['mean'] = grp.transform('mean')
    data['std'] = grp.transform('std')
    return data


def plot_all_item1():
    """Produce all plots for the iTEM1 database."""
    from plotnine import aes, geom_bar, facet_grid, labs

    from item.model import load_model_data, squash_scenarios
    from item.model.dimensions import ALL, PAX

    class pass_energy_use_mode(Plot):
        """Passenger energy use by mode.

        This reproduces a figure from the (private) item2-scripts respository.
        """
        variable = 'energy'
        selectors = dict(region='Global', mode=PAX, tech=ALL,
                         fuel=ALL, year=[2015, 2030, 2050])
        terms = [
            aes('year', 'value / 1000', fill='mode'),
            geom_bar(stat='identity'),
            facet_grid(['scenario', 'model']),
            labs(x='Year', y='EJ/year'),
            ]

    df = load_model_data(1)
    df = squash_scenarios(df, 1)
    pass_energy_use_mode(df, 1).save()


class Plot:
    """Plot class.

    Subclass Plot, overriding the variables below and optionally
    the filter() method, to create plots.
    """
    # Variable to select
    variable = ''

    # Other selectors to subset the data
    selectors = {}

    # Sequence of plotnine.ggplot terms
    terms = []

    def __init__(self, data, *fn_extra):
        # Select the data
        data = select(data, self.variable, **self.select)

        # Filter the data
        self.data = self.filter(data)

        print(data.describe())

        pre_terms = [ggplot(self.data), aes(**self.map)]

        # Produce both the aesthetic mapping and the labels from
        # the same class variable
        labels = {}
        for k, v in self.map.items():
            if v in INDEX:
                labels[k] = v.title()

            if v == 'value':
                var = self.data['variable'].unique()
                assert len(var) == 1
                var_info = INFO['variable'][var[0]]
                labels[k] = '{} [{}]'.format(var[0], var_info['unit'])

        # Chain together the terms to produce the figure
        terms = chain(pre_terms, self.terms, [labs(**labels)])
        fig = reduce(operator.add, terms)

        # Compose the filename
        clsname = [self.__class__.__name__]
        fn_extra = map(str, fn_extra)
        name = '_'.join(chain(clsname, fn_extra))
        self.filename = join(paths['plot'], '%s.%s' % (name, 'pdf'))

        # Save
        fig.save(self.filename, width=128, height=96, units='mm')

    def filter(self, data):
        """Override this method to filter or transform the selected data."""
        return data
