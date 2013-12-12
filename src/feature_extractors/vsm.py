#!/usr/bin/python

import collections
import codecs
import sys
import feature_extractor
import generic_vspace

def REGISTER_ARGUMENTS(parser):
  parser.add_argument("--append_VSM_features", default=False,
      action="store_true", help="Append VSM features")
  parser.add_argument("--VSM_filename", help="VSM filename")


class VSM(generic_vspace.GenericVectorSpace):
  def __init__(self, vectorSpaceUniqName, vectFileName, translation_dict):
    generic_vspace.GenericVectorSpace.__init__(
        self, vectorSpaceUniqName, vectFileName, translation_dict)

  def ExtractFeaturesFromInstance(
      self, filename, line_num, rel_type, sub, verb, obj):
    feature_dict = {}
    if not sub.is_none:
      feature_dict.update(self._WordToFeature(sub.lemma, 's'))
    if not verb.is_none:
      feature_dict.update(self._WordToFeature(verb.lemma, 'v'))
    if not obj.is_none:
      feature_dict.update(self._WordToFeature(obj.lemma, 'o'))
    return feature_dict
   
if __name__ == '__main__':
  print "This module is a library, not supposed to be executed directly."
  sys.exit(1)

def REGISTER_FEATURE_EXTRACTOR(args, translation_dict=None):
  if not args.append_VSM_features:
    return None
  return VSM('VSM', args.VSM_filename, translation_dict)
  
