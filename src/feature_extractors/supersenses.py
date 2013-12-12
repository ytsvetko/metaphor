#!/usr/bin/python

from __future__ import division
import collections
import codecs
import sys
import json
import feature_extractor

def REGISTER_ARGUMENTS(parser):
  parser.add_argument("--append_supersenses", default="",
      help="Comma-separated list of parts of speech for which append supersenses")
  parser.add_argument("--adj_supersenses", help="Adj supersense vocab")
  parser.add_argument("--noun_supersenses", help="Noun supersense vocab")
  parser.add_argument("--verb_supersenses", help="Verb supersense vocab")


class Supersenses(feature_extractor.FeatureExtractor):
  def __init__(self, vocabs, translation_dict):
    self.vocabs = vocabs
    self.translation_dict = translation_dict

  def _GetSupersensesByWord(self, word, pos):
    if pos not in self.vocabs:
      return {}
    vocab = self.vocabs[pos]
    if self.translation_dict is None:
      words = [word]
    else:
      words = self.translation_dict.Get(word)
    counters = collections.Counter()
    for w in words:
      for k,v in vocab.get(w, {}).iteritems():
        counters[k] += v
    return counters

  def _WordToFeature(self, word, relation, pos):
    counters = self._GetSupersensesByWord(word, pos)
    total = sum(counters.values())
    result = {}
    for supersense, count in counters.iteritems():
      result["SUP_{0}_{1}".format(relation, supersense)] = count / total
    return result

  def ExtractFeaturesFromInstance(
      self, filename, line_num, rel_type, sub, verb, obj):
    feature_dict = {}
    if rel_type == 'svo':
      if not sub.is_none:
        feature_dict.update(self._WordToFeature(sub.lemma, "SUB", "noun"))
      if not verb.is_none:
        feature_dict.update(self._WordToFeature(verb.lemma, "VERB", "verb"))
      if not obj.is_none:
        feature_dict.update(self._WordToFeature(obj.lemma, "OBJ", "noun"))
    else:
      assert rel_type == 'an', rel_type
      feature_dict.update(self._WordToFeature(sub.lemma, "ADJ", "adj"))
      feature_dict.update(self._WordToFeature(obj.lemma, "NOUN", "noun"))
    return feature_dict


def LoadVocab(filename):
  vocab = {}
  for line in codecs.open(filename, "r", "utf-8"):
    word, posteriors = line.strip().split("\t")
    feature_dict = {k:v for k, v in json.loads(posteriors).iteritems()}
    vocab[word] = feature_dict
  return vocab

    
def REGISTER_FEATURE_EXTRACTOR(args, translation_dict=None):
  active_supersenses = set([w.strip() for w in args.append_supersenses.split(",")])
  for pos in active_supersenses:
    assert pos in ['noun', 'adj', 'verb'], "Unknown pos: " + pos
  if len(active_supersenses) == 0:
    return None
  vocabs = {}
  vocabs['noun'] = LoadVocab(args.noun_supersenses) if 'noun' in active_supersenses else {}
  vocabs['adj'] = LoadVocab(args.adj_supersenses) if 'adj' in active_supersenses else {}
  vocabs['verb'] = LoadVocab(args.verb_supersenses) if 'verb' in active_supersenses else {}
  return Supersenses(vocabs, translation_dict)


if __name__ == '__main__':
  print "This module is a library, not supposed to be executed directly."
  sys.exit(1)

