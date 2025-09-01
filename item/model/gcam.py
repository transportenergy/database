from .common import ModelInfo

INFO = ModelInfo(
    id="gcam",
    citation="""
    @techreport{mishra-2013,
      author = {Gouri Shankar Mishra and Page Kyle and Jacob Teter and Geoffrey Morrison and S. Kim and Sonia Yeh},
      institution = {Institute of Transportation Studies, University of California, Davis},
      location = {Davis, CA, US},
      number = {UCD-ITS-RR-13-05},
      title = {{Transportation Module of Global Change Assessment Model (GCAM): Model Documentation}},
      type = {Research Report},
      url = {http://www.its.ucdavis.edu/research/publications/publication-detail/?pub_id=1884},
      year = {2013}
    }""",
    format="csv",
    versions=(1, 2, 3),
)
