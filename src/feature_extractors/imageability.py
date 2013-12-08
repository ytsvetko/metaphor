#!/usr/bin/python

import collections
import sys
import feature_extractor
import codecs

def REGISTER_ARGUMENTS(parser):
  parser.add_argument("--append_imageability_features", action="store_true",
      help="Append adjective imageability features")
  parser.add_argument("--imageability_predictions_filename", default=None,
      help="Imageability predictions filename")
  parser.add_argument("--imageability_prediction_A_threshold", default=0.6,
      type=float, help="Imageability predictions - threshold")

class ImageabilityPredictions:
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


class ImageabilityFeatureExtractor(feature_extractor.FeatureExtractor):
  def __init__(self, predictions_filename, a_threshold):
    self.predictions = ImageabilityPredictions(
        predictions_filename, a_threshold)

  def _MakeFeatures(self, word, role):
    result = {}
    threshold_label = "?"
    predictions_tuple = self.predictions.Get(word)
    if predictions_tuple is not None:
      label, threshold_label, score_A, score_C = predictions_tuple
      result["Imageability_{}_threshold_{}".format(role, threshold_label)] = 1
      result["Imageability_{}_unimg".format(role)] = score_A
      result["Imageability_{}_img".format(role)] = score_C
    return result, threshold_label

  def ExtractFeaturesFromInstance(
      self, filename, line_num, line, rel_type, adj, verb, obj):
    feature_dict = {}
    if rel_type == 'an':
      if not adj.is_none:
        adj_dict, adj_label = self._MakeFeatures(adj.lemma, "ADJ")
        feature_dict.update(adj_dict)
    return feature_dict
   
    
if __name__ == '__main__':
  print "This module is a library, not supposed to be executed directly."
  sys.exit(1)

def REGISTER_FEATURE_EXTRACTOR(args, traslation_dict=None):
  if not args.append_imageability_features:
    return None
  if args.imageability_predictions_filename is None:
    print "Flag --imageability_predictions_filename is required"
    sys.exit(1)
  return ImageabilityFeatureExtractor(args.imageability_predictions_filename,
                                      args.imageability_prediction_A_threshold)
  
