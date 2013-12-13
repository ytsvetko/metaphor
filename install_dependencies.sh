#!/bin/bash

#set -o xtrace
export ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

INSTALL_TURBO_PARSER=1
INSTALL_NLTK=0
INSTALL_SKLEARN=0
INSTALL_AOT_PARSER=0 # Russian parser

#===============================================================================
# INSTALL TURBO PARSER
if [ "${INSTALL_TURBO_PARSER}" == "1" ] ; then
  mkdir -p tools
  cd tools
  wget http://www.cs.cmu.edu/~afm/TurboParser/TurboParser-2.1.0.tar.gz
  tar -zxvf TurboParser-2.1.0.tar.gz
  cd tools/TurboParser-2.1.0
  mkdir -p models/english_proj
  cd models/english_proj
  wget https://www.ark.cs.cmu.edu/TurboParser/sample_models/english_proj_tagger.tar.gz
  tar -zxvf english_proj_tagger.tar.gz
  wget https://www.ark.cs.cmu.edu/TurboParser/sample_models/english_proj_parser.tar.gz
  tar -zxvf english_proj_parser.tar.gz
  rm english_proj_tagger.tar.gz english_proj_parser.tar.gz 
  cd - 
  ./install_deps.sh
  ./configure && make && make install
  export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:`pwd;`/deps/local/lib:"
  cd ../../
fi

#===============================================================================
# INSTALL NLTK
if [ "${INSTALL_NLTK}" == "1" ] ; then
  # Install Pip: 
  sudo easy_install pip
  # Install Numpy
  sudo pip install -U numpy
  # Install PyYAML and NLTK
  sudo pip install -U pyyaml nltk
fi

#===============================================================================
# INSTALL_SKLEARN
if [ "${INSTALL_SKLEARN}" == "1" ] ; then
  sudo pip install scikit-learn
fi

#===============================================================================

