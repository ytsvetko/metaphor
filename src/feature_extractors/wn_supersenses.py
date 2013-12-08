#!/usr/bin/python

from __future__ import division
import collections
import codecs
import sys
import feature_extractor
from nltk.corpus import wordnet as wn

def REGISTER_ARGUMENTS(parser):
  parser.add_argument("--append_wn_supersenses", action="store_true",
      help="Append WordNet supersense features")

"""
Types of supersenses for Nouns and Verbs:

ABSTRACT_LEX_IDS = set(["noun.cognition", "noun.communication","noun.feeling", "noun.motive", "noun.possession",  "noun.quantity", "noun.relation",  "noun.state", "noun.time",  "verb.change", "verb.cognition", "verb.emotion", "verb.perception", "verb.social"])

CONCRETE_LEX_IDS = set(["noun.animal", "noun.artifact", "noun.body","noun.location", "noun.object", "noun.person", "noun.phenomenon", "noun.plant", "noun.shape",  "noun.substance", "verb.body", "verb.communication", "verb.competition", "verb.consumption", "verb.contact",  "verb.motion",  "verb.possession", "verb.weather"])
"""

class WordNetSupersenseFeatureExtractor(feature_extractor.FeatureExtractor):
  def __init__(self, translation_dict=None):
    self.wordnet_parser = wordnet_parser.WordNetParser(
        data_file_name=wordnet_data_file)
    self.translation_dict = translation_dict

  def _GetSupersensesByWord(self, word, ss_type):    
    if self.translation_dict is None:
      words = [word]
    else:
      words = self.translation_dict.Get(word)
    counters = collections.Counter()
    for w in words:
      for synset in wn.synsets(word, ss_type):
        counters[synset.lexname] += 1
    return counters

  def _WordToFeature(self, word, relation, ss_type):
    counters = self._GetSupersensesByWord(word, ss_type)
    total = sum(counters.values())
    result = {}
    for supersense, count in counters.iteritems():
      result["WN_Supersense_{0}_{1}".format(relation, supersense)] = count / total
    return result

  def ExtractFeaturesFromInstance(
      self, filename, line_num, line, rel_type, sub, verb, obj):
    feature_dict = {}
    if rel_type = 'svo':
      if not sub.is_none:
        feature_dict.update(self._WordToFeature(sub.lemma, "SUB", wn.NOUN))
      if not verb.is_none:
        feature_dict.update(self._WordToFeature(verb.lemma, "VERB", wn.VERB))
    if not obj.is_none:
      feature_dict.update(self._WordToFeature(obj.lemma, "OBJ", wn.NOUN))
    return feature_dict
   
    
if __name__ == '__main__':
  print "This module is a library, not supposed to be executed directly."
  sys.exit(1)

def REGISTER_FEATURE_EXTRACTOR(args, traslation_dict=None):
  if not args.append_wn_supersenses:
    return None
  return WordNetSupersenseFeatureExtractor(translation_dict)
  
