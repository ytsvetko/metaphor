#!/usr/bin/python

import collections
import codecs
import sys
import json
import feature_extractor

def REGISTER_ARGUMENTS(parser):
  parser.add_argument("--append_adj_supersense_features", action="store_true",
      help="Append Adj supersense features")
  parser.add_argument("--adj_supersense_vocab", help="Adj supersense vocab")

class AdjSupersenses(feature_extractor.FeatureExtractor):
  def __init__(self, supersense_vocab_file, translation_dict):
    self.vocab_predictions = {}
    for line in codecs.open(supersense_vocab_file, "r", "utf-8"):
      instance, prediction, posteriors = line.strip().split("\t")
      feature_dict = {"ADJ_SUP_" + k:v for k, v in json.loads(posteriors).iteritems()}
      feature_dict["count"] = 1   # temporary
      word = instance.split("_", 1)[0]
      if translation_dict is None:
        words = [word]
      else:
        words = translation_dict.Get(word)
      for w in words:
        existing = self.vocab_predictions.setdefault(w, {})
        for k, v in feature_dict.iteritems():
          old = existing.get(k, 0.0)
          existing[k] = old + v
    for w, feature_dict in self.vocab_predictions.iteritems():
      count = feature_dict['count']
      del feature_dict['count']
      for k in feature_dict:
        feature_dict[k] /= count

  def ExtractFeaturesFromInstance(self, filename, line_num, line, rel_type, adj, unused, noun):
    feature_dict = {}
    if rel_type == 'an':
      if not adj.is_none:
        feature_dict.update(self.vocab_predictions.get(adj.word, {}))
    return feature_dict
   
if __name__ == '__main__':
  print "This module is a library, not supposed to be executed directly."
  sys.exit(1)

def REGISTER_FEATURE_EXTRACTOR(args, traslation_dict=None):
  if not args.append_adj_supersense_features:
    return None   
  return AdjSupersenses(args.adj_supersense_vocab, translation_dict)
  
