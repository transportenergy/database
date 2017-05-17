from matplotlib import rc
from plotnine import aes, ggplot, geom_bar, facet_grid, labs

from item.model import select
from item.model.dimensions import ALL, PAX


rc('text', usetex=False)


def plot_all_item1():
    """Produce all plots for the iTEM1 database."""
    from item.model import load_model_data

    data = load_model_data(1)
    plot_pass_energy_use_mode(data)


def plot_pass_energy_use_mode(data):
    """Passenger energy use by mode.

    This reproduces a figure from the (private) item2-scripts respository.
    """
    data = select(data, 'energy', region='Global', mode=PAX, tech=ALL,
                  fuel=ALL, year=[2015, 2030, 2050])

    # TODO add palette
    # TODO exclude 2015 Policy values
    plot = (ggplot(data, aes('year', 'value / 1000', fill='mode'))
            + geom_bar(stat='identity')
            + facet_grid(['scenario', 'model'])
            + labs(x='Year', y='EJ/year'))

    plot.save('pass_energy_use_mode.pdf')
