$CACHE/$CONDAFNAME -b -u -p $HOME/miniconda
conda info --all

pip install -r ci/requirements.txt

# NB must do this here because Travis does not handle 'r_binary_packages' until
#    *after* the install: script in .travis.yml
sudo apt-get install -y r-cran-devtools
