import pandas as pd

from .common import ModelInfo

INFO = ModelInfo(
    id="message",
    citation="""
    @article{mccollum-2017,
      author = {David L. McCollum and Charlie Wilson and Hazel Pettifor and Kalai Ramea and Volker Krey and Keywan Riahi and Christoph Bertram and Zhenhong Lin and Oreane Y. Edelenbosch and Sei Fujisawa},
      doi = {10.1016/j.trd.2016.04.003},
      issn = {1361-9209},
      journalsubtitle = {Transport and Environment},
      journaltitle = {Transportation Research Part D},
      keywords = {Consumer choice; Human behavior; Transport; Light-duty vehicles; Climate change mitigation},
      pages = {322–342},
      subtitle = {An application to consumers’ vehicle choices},
      title = {Improving the behavioral realism of global integrated assessment models},
      volume = {55},
      year = {2017},
    }""",
    format="xlsx",
    org="International Institute for Applied Systems Analysis (IIASA)",
    versions=(1, 2),
)


def import_data(data_path, metadata_path):
    input_fn = data_path

    data = pd.read_excel(input_fn, sheetname=["data_Base", "data_2C"])

    # Read comments sheet
    notes = (
        pd.read_excel(input_fn, "comments")
        .dropna(subset=["comments"])
        .drop(["Scenario", "Region"], axis="columns")
    )
    notes["Model"] = "MESSAGE"

    return pd.concat(data.values()), None
