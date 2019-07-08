$CACHE/$CONDAFNAME -b -u -p $HOME/miniconda
conda info --all
which -a p

pip install -r ci/requirements.txt

# Remove the package if it has been cached
pip uninstall item


# NB must do this here because Travis does not handle 'r_binary_packages' until
#    *after* the install: script in .travis.yml
sudo apt-get install -y r-cran-devtools
