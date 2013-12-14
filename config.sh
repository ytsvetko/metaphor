#!/bin/bash

# Export paths for various tools, resources, and variables specific to the project

# Tools
if [ `uname -n` == "allegro.clab.cs.cmu.edu" ] ; then
  export TURBO_PARSER_DIR=/usr0/home/ytsvetko/tools/TurboParser-2.1.0
  export SEMAN_PARSER_DIR=/usr0/home/ytsvetko/tools/aot/seman/trunk
elif [ `uname -n` == "ur.lti.cs.cmu.edu" ] ; then
  export TURBO_PARSER_DIR=/usr1/project/METAL/tools/TurboParser-2.0.1
  export SEMAN_PARSER_DIR=/usr1/project/METAL/tools/AOTParser
elif [ `uname -n` == "leo-Inspiron-1525" ] ; then
  export TURBO_PARSER_DIR=/home/leo/TurboParser-2.0.1
  export SEMAN_PARSER_DIR=/home/leo/SourceTree/AOT/seman-svn/trunk
else
  export TURBO_PARSER_DIR=${ROOT_DIR}/tools/TurboParser-2.1.0
  export SEMAN_PARSER_DIR=${ROOT_DIR}/tools/aot/seman/trunk
  # TODO export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:`pwd;`/deps/local/lib:"
fi

if [ ! ${ROOT_DIR} = "" ] ; then 
  # Scripts
  export BIN_DIR=${ROOT_DIR}/src

  # Trained models
  AN_MODEL=${ROOT_DIR}/models/an.model
  SVO_MODEL=${ROOT_DIR}/models/svo.model

  # Resources
  export RESOURCE_DIR=${ROOT_DIR}/resources

  export ABSTRACTNESS=${RESOURCE_DIR}/abstractness/en/abstractness.predictions
  export IMAGEABILITY=${RESOURCE_DIR}/imageability/en/imageability.predictions  
  export NOUN_SUPERSENSES=${RESOURCE_DIR}/supersenses/wn_noun.supersneses
  export VERB_SUPERSENSES=${RESOURCE_DIR}/supersenses/wn_verb.supersneses
  export ADJ_SUPERSENSES=${RESOURCE_DIR}/supersenses/wn_adj.supersneses
  export VSM=${RESOURCE_DIR}/VSM/en-svd-de-64.txt
  export FILTER_FILES_DIR=${RESOURCE_DIR}/filters

  # Training data
  export SVO_MET=${RESOURCE_DIR}/TroFi/literal.txt
  export SVO_NONMET=${RESOURCE_DIR}/TroFi/metaphorical.txt
  export AN_MET=${RESOURCE_DIR}/AdjN/training_adj_noun_met_en.txt
  export AN_NONMET=${RESOURCE_DIR}/AdjN/training_adj_noun_nonmet_en.txt
fi

# Metaphor detection pipelines
export RUN_SVO=1
export RUN_AN=1
export RUN_NN=0

export ABSTRACTNESS_THRESHOLD=0.8
export IMAGEABILITY_THRESHOLD=0.9
export SVO_LABEL_WEIGHTS="{'L': 0.58, 'M': 0.42}"
export AN_LABEL_WEIGHTS="{'L': 1.0, 'M': 1.0}"

# Data parameters to the extract_instances.py.
EXTRACT_FEATURES_PARAMS=""
EXTRACT_FEATURES_PARAMS+="--VSM_filename=${VSM} "
EXTRACT_FEATURES_PARAMS+="--adj_supersenses=${ADJ_SUPERSENSES} "
EXTRACT_FEATURES_PARAMS+="--noun_supersenses=${NOUN_SUPERSENSES} "
EXTRACT_FEATURES_PARAMS+="--verb_supersenses=${VERB_SUPERSENSES} "
EXTRACT_FEATURES_PARAMS+="--abstractness_predictions_filename=${ABSTRACTNESS} "
EXTRACT_FEATURES_PARAMS+="--abstractness_prediction_A_threshold=${ABSTRACTNESS_THRESHOLD} "
EXTRACT_FEATURES_PARAMS+="--imageability_predictions_filename=${IMAGEABILITY} "
EXTRACT_FEATURES_PARAMS+="--imageability_prediction_A_threshold=${IMAGEABILITY_THRESHOLD} "

TODO_UNSUPPORTED='
# Which features should be extracted in this experiment.
# Set to 1 features you want to be included in this experiment.
export ADD_SUPERSENSE_FEATURES=1
export ADD_ABSTRACTNESS_FEATURES=1
export ADD_IMAGEABILITY_FEATURES=1
export ADD_NAMED_ENTITIES_FEATURES=0
export ADD_VSM_FEATURES=1

# The lines below create the command line parameters for the extract_instances.py
# based on the parameters above.
# NOTE: Do not forget to append an extra space after each parameter.

if [ "${ADD_SUPERSENSE_FEATURES}" == "1" ] ; then
  EXTRACT_FEATURES_PARAMS+="--append_wn_supersenses "
  EXTRACT_FEATURES_PARAMS+="--append_adj_supersense_features "
fi
if [ "${ADD_ABSTRACTNESS_FEATURES}" == "1" ] ; then  
  EXTRACT_FEATURES_PARAMS+="--append_abstractness_features "
fi
if [ "${ADD_IMAGEABILITY_FEATURES}" == "1" ] ; then
  EXTRACT_FEATURES_PARAMS+="--append_imageability_features "
fi
if [ "${ADD_VSM_FEATURES}" == "1" ] ; then
  EXTRACT_FEATURES_PARAMS+="--append_VSM_features "
fi
'

export EXTRACT_FEATURES_PARAMS


