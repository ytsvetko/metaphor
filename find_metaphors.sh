#!/bin/bash

#set -o xtrace
export ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source ${ROOT_DIR}/config.sh


if [ "$#" -ne 1 ] || ! [ -f "$1" ]; then
  echo "Usage: $0 path_to_file" >&2
  exit 1
fi

if [ ! -d "${TURBO_PARSER_DIR}" ] ; then 
  echo "Please, update a path to Turbo Parser -- TURBO_PARSER_DIR variable in config.sh " >&2
  exit 1  
fi

INPUT_FILE=$1

WORK_DIR=${ROOT_DIR}/work
mkdir -p ${WORK_DIR}
 
OUTPUT_DIR=${ROOT_DIR}/output
mkdir -p ${OUTPUT_DIR}

OUTPUT_FILE=${OUTPUT_DIR}/`basename $INPUT_FILE`.metaphors


#1. Run Turbo Parser on a text file split to sentences.
echo "Parsing input"
PARSED_INPUT_FILE=${WORK_DIR}/`basename $INPUT_FILE`.parsed
if [ ! -f ${PARSED_INPUT_FILE} ]; then
  echo "Parsing "$INPUT_FILE" with Turbo parser ..."
  ${TURBO_PARSER_DIR}/scripts/parse.sh $INPUT_FILE > ${PARSED_INPUT_FILE}
fi

#2. Convert Turbo Parser output into internal format of instances.
#   Separate files for SVO and AN.
if [ ${RUN_SVO} = 1 ] ; then
  SVO_CANDIDATES_FILE=${WORK_DIR}/`basename $INPUT_FILE`.svo_candidates
  ${BIN_DIR}/parse_turbo_output.py --turbo_filename ${PARSED_INPUT_FILE} \
                                   --out_file ${SVO_CANDIDATES_FILE} \
                                   --rel_type svo
fi
if [ ${RUN_AN} = 1 ] ; then
  AN_CANDIDATES_FILE=${WORK_DIR}/`basename $INPUT_FILE`.an_candidates
  ${BIN_DIR}/parse_turbo_output.py --turbo_filename ${PARSED_INPUT_FILE} \
                                   --out_file ${AN_CANDIDATES_FILE} \
                                   --rel_type an
fi

#3. Run each through feature extraction.
#   Different parameters for each mode (SVO or AN).
echo "Extracting features"
if [ ${RUN_SVO} = 1 ] ; then
  SVO_FEATURES=${WORK_DIR}/`basename $INPUT_FILE`.svo_features
  ${BIN_DIR}/extract_instances.py --input_file ${SVO_CANDIDATES_FILE} \
                                  --features_filename ${SVO_FEATURES} \
                                  --labels_filename /dev/null \
                                  --append_supersenses="noun,verb" \
                                  --append_abstractness_features \
                                  --append_VSM_features \
                                  ${EXTRACT_FEATURES_PARAMS}
fi
if [ ${RUN_AN} = 1 ] ; then
  AN_FEATURES=${WORK_DIR}/`basename $INPUT_FILE`.an_features
  ${BIN_DIR}/extract_instances.py --input_file ${AN_CANDIDATES_FILE} \
                                  --features_filename ${AN_FEATURES} \
                                  --labels_filename /dev/null \
                                  --append_supersenses="noun,adj" \
                                  --append_abstractness_features \
                                  --append_imageability_features \
                                  --append_VSM_features \
                                  ${EXTRACT_FEATURES_PARAMS}
fi


# 4. Run classifier trained for each mode separately.
echo "Running classifier"
if [ ${RUN_SVO} = 1 ] ; then
  SVO_PREDICTED=${WORK_DIR}/`basename $INPUT_FILE`.svo_predicted
  ${BIN_DIR}/classify.py --load_classifier_filename ${SVO_MODEL} \
       --test_features ${SVO_FEATURES} \
       --test_predicted_labels_out ${SVO_PREDICTED}
fi

if [ ${RUN_AN} = 1 ] ; then
  AN_PREDICTED=${WORK_DIR}/`basename $INPUT_FILE`.an_predicted
  ${BIN_DIR}/classify.py --load_classifier_filename ${AN_MODEL} \
       --test_features ${AN_FEATURES} \
       --test_predicted_labels_out ${AN_PREDICTED}
fi

echo "Writing output to "${OUTPUT_FILE}
echo "Output format: sentence \t label (M or L) \t labeled metaphor candidates in json format"
${BIN_DIR}/format_output.py --input_file ${INPUT_FILE} \
       --predicted_an_label ${AN_PREDICTED} \
       --predicted_svo_label ${SVO_PREDICTED} \
       --filter_files_dir ${FILTER_FILES_DIR} \
       --out_file ${OUTPUT_FILE}


