import T001


SCRIPTS = {
    1: T001.process
}


def process(id):
    """Process a data set given its *id*."""
    # TODO perform common loading tasks

    # Call the dataset-specific processing
    script = SCRIPTS[1]
    df = script()

    # TODO perform common cleaning tasks

    return df
