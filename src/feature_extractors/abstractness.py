#!/usr/bin/env python2.7

import collections
import sys
import feature_extractor
import codecs

def REGISTER_ARGUMENTS(parser):
  parser.add_argument("--append_abstractness_features", action="store_true",
      help="Append abstractness features")
  parser.add_argument("--abstractness_predictions_filename", default=None,
      help="Abstractness predictions filename")
  parser.add_argument("--abstractness_prediction_A_threshold", default=0.6,
      type=float, help="Abstractness predictions - threshold")

class AbstractnessPredictions:
  def __init__(self, filename, a_threshold):
    self.word_predictions = collections.defaultdict(list)
    for line in codecs.open(filename, "r", "utf-8"):
      word, label, predictions = line.strip().split("\t")
      predictions_dict = eval(predictions)
      score_A = predictions_dict["A"]
      score_C = predictions_dict["C"]
      threshold_label = "A" if score_A >= a_threshold else "C"
      self.word_predictions[word].append( (label, threshold_label, score_A, score_C) )

  def Get(self, word):
    if word not in self.word_predictions:
      return None
    predictions_list = self.word_predictions[word]
    C_count = 0
    max_C = None
    max_A = None
    for prediction_tuple in predictions_list:
      label, threshold_label, score_A, score_C = prediction_tuple
      if label == "C":
        C_count += 1
        if max_C is None or max_C[3] < score_C:
          max_C = prediction_tuple
      else:
        if max_A is None or max_A[2] < score_A:
          max_A = prediction_tuple
    if C_count * 2 >= len(predictions_list):
      return max_C
    return max_A


class AbstractnessFeatureExtractor(feature_extractor.FeatureExtractor):
  def __init__(self, predictions_filename, a_threshold):
    self.abstractness_predictions = AbstractnessPredictions(
        predictions_filename, a_threshold)

  def _MakeFeatures(self, word, role):
    result = {}
    threshold_label = "?"
    predictions_tuple = self.abstractness_predictions.Get(word)
    if predictions_tuple is not None:
      label, threshold_label, score_A, score_C = predictions_tuple
      result["Abstractness_{}_threshold_{}".format(role, threshold_label)] = 1
      result["Abstractness_{}_Abs".format(role)] = score_A
      result["Abstractness_{}_Conc".format(role)] = score_C
    return result, threshold_label

  def ExtractFeaturesFromInstance(
      self, filename, line_num, rel_type, sub, verb, obj):
    feature_dict = {}
    verb_dict, verb_label = {}, "?"
    sub_dict, sub_label = {}, "?"
    obj_dict, obj_label = {}, "?"
    if not verb.is_none:
      verb_dict, verb_label = self._MakeFeatures(verb.lemma, "VERB")
    if not sub.is_none:
      sub_dict, sub_label = self._MakeFeatures(sub.lemma, "SUB")
      if verb_label != "?" and sub_label != "?":
        feature_dict["Abstractness_cross_SV_{}{}".format(sub_label, verb_label)] = 1
      feature_dict.update(sub_dict)
    feature_dict.update(verb_dict)
    if not obj.is_none:
      obj_dict, obj_label = self._MakeFeatures(obj.lemma, "OBJ")
      feature_dict.update(obj_dict)
      if verb_label != "?" and obj_label != "?":
        feature_dict["Abstractness_cross_OV_{}{}".format(obj_label, verb_label)] = 1
    if sub_label != "?" and verb_label == "?" and obj_label != "?":
      feature_dict["Abstractness_cross_SO_{}{}".format(sub_label, obj_label)] = 1
    return feature_dict


if __name__ == '__main__':
  print "This module is a library, not supposed to be executed directly."
  sys.exit(1)

def REGISTER_FEATURE_EXTRACTOR(args, traslation_dict=None):
  if not args.append_abstractness_features:
    return None
  if args.abstractness_predictions_filename is None:
    print "Flag --abstractness_predictions_filename is required"
    sys.exit(1)
  return AbstractnessFeatureExtractor(
      args.abstractness_predictions_filename,
      args.abstractness_prediction_A_threshold)
  
