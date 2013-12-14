#!/bin/bash

#set -o xtrace
export ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source ${ROOT_DIR}/config.sh

if [ "$#" -ne 4 ] || ! [ -f "$3" ] || ! [ -f "$4" ]; then
  echo "Parameters:" >&2
  echo "    1. relation type (svo or an)" >&2
  echo "    2. format of the training files (input-text or input-rel)" >&2
  echo "    3. path to metaphoric training file" >&2
  echo "    4. path to literal training file" >&2
  echo "" >&2
  echo "Examples:" >&2
  echo "  $0 svo input-text resources/TroFi/metaphorical.txt resources/TroFi/literal.txt" >&2
  echo "  $0 an input-rel resources/AdjN/training_adj_noun_met_en.txt resources/AdjN/training_adj_noun_nonmet_en.txt" >&2
  exit 1
fi


# Train model for SVO or AdjN relations
# Input - training corpus
MODE=$1
INPUT_TYPE=$2
TRAINNING_MET_FILE=$3
TRAINNING_LIT_FILE=$4

WORK_DIR=${ROOT_DIR}/work/${MODE}
mkdir -p ${WORK_DIR}

function TurboParse {
  in_file=$1
  parsed_file=${WORK_DIR}/`basename $in_file`.parsed
  if [ ! -f ${parsed_file} ]; then
    ${TURBO_PARSER_DIR}/scripts/parse.sh $in_file > ${parsed_file}
  fi
  instances_file=${WORK_DIR}/`basename $in_file`
  EXTRA_PARAMS=""
  if [ "${MODE}" == "svo" ]; then
    EXTRA_PARAMS+="--filter_verbs_filename ${RESOURCE_DIR}/TroFi/trofi_verbs.txt"
  fi
  ${BIN_DIR}/parse_turbo_output.py --turbo_filename ${parsed_file} \
                                   --out_file ${instances_file} \
                                   --rel_type ${MODE} \
                                   ${EXTRA_PARAMS}
}

function RelParse {
  in_file=$1
  instances_file=${WORK_DIR}/`basename ${in_file}`
  ${BIN_DIR}/parse_relations.py --input_file ${in_file} \
                                --out_file ${instances_file} \
                                --rel_type ${MODE}
}

echo "Parsing input"
#1. Run Turbo Parser on a text file split to sentences.
if [ ${INPUT_TYPE} = "input-text" ] ; then
  TurboParse ${TRAINNING_MET_FILE}
  TurboParse ${TRAINNING_LIT_FILE}
fi

#1. Create input relations into internal format of instances..
if [ ${INPUT_TYPE} = "input-rel" ] ; then
  RelParse ${TRAINNING_MET_FILE}
  RelParse ${TRAINNING_LIT_FILE}
fi

function ExtractFeatures {
  in_file=$1
  label=$2
  instances_file=${WORK_DIR}/`basename ${in_file}`
  labels_file=${WORK_DIR}/`basename ${in_file}`".labels"
  features_file=${WORK_DIR}/`basename ${in_file}`".features"
  if [ ${MODE} = "svo" ] ; then
  ${BIN_DIR}/extract_instances.py --input_file ${instances_file} \
                                  --features_filename ${features_file} \
                                  --labels_filename ${labels_file} \
                                  --append_supersenses="noun,verb" \
                                  --append_abstractness_features \
                                  --append_VSM_features \
                                  --label ${label} \
                                  --blacklisted_instances resources/TroFi/to_filter \
                                  ${EXTRACT_FEATURES_PARAMS}
  fi

  if [ ${MODE} = "an" ] ; then
  ${BIN_DIR}/extract_instances.py --input_file ${instances_file} \
                                  --features_filename ${features_file} \
                                  --labels_filename ${labels_file} \
                                  --append_supersenses="noun,adj" \
                                  --append_abstractness_features \
                                  --append_imageability_features \
                                  --append_VSM_features \
                                  --label ${label} \
                                  ${EXTRACT_FEATURES_PARAMS}
  fi
}

#2. Run each through feature extraction.
#   Different parameters for each mode (SVO or AN).
echo "Extracting features"
ExtractFeatures ${TRAINNING_MET_FILE} M
ExtractFeatures ${TRAINNING_LIT_FILE} L

# 4. Run classifier trained for each mode separately.
function TrainClassifier {
  out_model_file=$1

  labels_file=${WORK_DIR}/train.labels
  feat_file=${WORK_DIR}/train.feat

  cat ${WORK_DIR}/`basename ${TRAINNING_MET_FILE}`".features" > ${feat_file}
  cat ${WORK_DIR}/`basename ${TRAINNING_LIT_FILE}`".features" >> ${feat_file}

  cat ${WORK_DIR}/`basename ${TRAINNING_MET_FILE}`".labels" > ${labels_file}
  cat ${WORK_DIR}/`basename ${TRAINNING_LIT_FILE}`".labels" >> ${labels_file}
  
  ${BIN_DIR}/classify.py \
      --train_features ${feat_file} --train_labels ${labels_file} \
      --num_cross_validation_folds 10 \
      --dump_classifier_filename ${out_model_file}
}

echo "Training models"
if [ ${MODE} = "svo" ]; then
  TrainClassifier ${SVO_MODEL}
fi
if [ ${MODE} = "an" ]; then
  TrainClassifier ${AN_MODEL}
fi

