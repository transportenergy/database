$CACHE/$CONDAFNAME -b -u -p $HOME/miniconda
conda info --all

which -a pip
pip install ci/requirements.txt
