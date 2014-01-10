#!/bin/bash

#set -o xtrace
export ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source ${ROOT_DIR}/config.sh


if [ "$#" -ne 2 ] || ! [ -f "$2" ]; then
  echo "Parameters:" >&2
  echo "    1. relation type (svo or an)" >&2
  echo "    2. path to the file" >&2
  exit 1
fi

if [ ! -d "${TURBO_PARSER_DIR}" ] ; then 
  echo "Please, update a path to Turbo Parser -- TURBO_PARSER_DIR variable in config.sh " >&2
  exit 1  
fi

MODE=$1
INPUT_FILE=$2

WORK_DIR=${ROOT_DIR}/work
mkdir -p ${WORK_DIR}

INSTANCES_FILE=${WORK_DIR}/`basename ${INPUT_FILE}`

OUTPUT_DIR=${ROOT_DIR}/output
mkdir -p ${OUTPUT_DIR}

OUTPUT_FILE=${OUTPUT_DIR}/`basename $INPUT_FILE`.metaphors

function RelParse {
  in_file=$1
  instances_file=$2
  ${BIN_DIR}/parse_relations.py --input_file ${in_file} \
                                --out_file ${instances_file} \
                                --rel_type ${MODE}
}

#1. Create input relations into internal format of instances..
echo "Parsing input"
RelParse ${INPUT_FILE} ${INSTANCES_FILE}


#2. Run feature extraction.
#   Different parameters for each mode (SVO or AN).
echo "Extracting features"
if [ ${MODE} = "svo" ] ; then
  SVO_FEATURES=${WORK_DIR}/`basename $INPUT_FILE`.svo_features
  ${BIN_DIR}/extract_instances.py --input_file ${INSTANCES_FILE} \
                                  --features_filename ${SVO_FEATURES} \
                                  --labels_filename /dev/null \
                                  --append_supersenses="noun,verb" \
                                  --append_abstractness_features \
                                  --append_VSM_features \
                                  ${EXTRACT_FEATURES_PARAMS}
fi
if [ ${MODE} = "an" ] ; then
  AN_FEATURES=${WORK_DIR}/`basename $INPUT_FILE`.an_features
  ${BIN_DIR}/extract_instances.py --input_file ${INSTANCES_FILE} \
                                  --features_filename ${AN_FEATURES} \
                                  --labels_filename /dev/null \
                                  --append_supersenses="noun,adj" \
                                  --append_abstractness_features \
                                  --append_imageability_features \
                                  --append_VSM_features \
                                  ${EXTRACT_FEATURES_PARAMS}
fi

# 3. Run classifier trained for each mode separately.
echo "Running classifier"
if [ ${MODE} = "svo" ] ; then
  SVO_PREDICTED=${WORK_DIR}/`basename $INPUT_FILE`.svo_predicted
  ${BIN_DIR}/classify.py --load_classifier_filename ${SVO_MODEL} \
       --test_features ${SVO_FEATURES} \
       --test_predicted_labels_out ${SVO_PREDICTED} \
       --write_posterior_probabilities \
       --label_weights "${SVO_LABEL_WEIGHTS}"
fi

if [ ${MODE} = "an" ] ; then
  AN_PREDICTED=${WORK_DIR}/`basename $INPUT_FILE`.an_predicted
  ${BIN_DIR}/classify.py --load_classifier_filename ${AN_MODEL} \
       --test_features ${AN_FEATURES} \
       --test_predicted_labels_out ${AN_PREDICTED} \
       --write_posterior_probabilities \
       --label_weights "${AN_LABEL_WEIGHTS}"
fi

echo "Writing output to "${OUTPUT_FILE}
echo "Output format: relation <tab> label (M or L) <tab> labeled metaphor candidates in json format"
if [ ${MODE} = "svo" ] ; then
  ${BIN_DIR}/format_output.py --input_file ${INPUT_FILE} \
       --predicted_an_label /dev/null \
       --predicted_svo_label ${SVO_PREDICTED} \
       --filter_files_dir ${FILTER_FILES_DIR} \
       --out_file ${OUTPUT_FILE}
fi
if [ ${MODE} = "an" ] ; then
  ${BIN_DIR}/format_output.py --input_file ${INPUT_FILE} \
       --predicted_an_label ${AN_PREDICTED} \
       --predicted_svo_label /dev/null \
       --filter_files_dir ${FILTER_FILES_DIR} \
       --out_file ${OUTPUT_FILE}
fi

