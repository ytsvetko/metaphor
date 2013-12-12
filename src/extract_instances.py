#!/usr/bin/env python2.7

import codecs
import sys
import glob
import os
import json
import feature_extractor

parser = feature_extractor.parser

# Use one of those two parameters to specify the inputs
parser.add_argument("--input_dir", help="Directory with input text files (output of parse_turbo_output.py)")
parser.add_argument("--input_file", help="Filename with input text file (output of parse_turbo_output.py)")
parser.add_argument("--features_filename", required=True, help="Output file with features in creg format")
parser.add_argument("--labels_filename", required=True, help="Output file with labels in creg format")
parser.add_argument("--blacklisted_instances", help="File with instances that should not be processed")
parser.add_argument("--skip_subject_null_instances", default=False, action='store_true')

args = feature_extractor.Repository.GetArgs()
feature_extractors = feature_extractor.Repository.GetActiveFeatureExtractors()

class TurboWord:
  def __init__(self, line):
    self.is_none = (line.strip().lower() == "none")
    if not self.is_none:
      tokens = line.split()
      self.lemma, self.surface_form, self.pos_tag, self.word_index = tokens[:4]
      self.word_index = int(self.word_index)
    else:
      #self.word_index = 999
      self.lemma, self.surface_form, self.pos_tag, self.word_index = (None, None, None, 999)

  def __unicode__(self):
    if self.is_none:
      return u"999_none_none"
    return u"{}_{}_{}".format(self.word_index, self.lemma, self.surface_form)

class InstanceExtractor:
  def __init__(self, feature_extractors, blacklisted_instances, features_file,
      labels_file):
    self.feature_extractors = feature_extractors
    self.blacklisted_instances = blacklisted_instances
    self.features_file = features_file
    self.labels_file = labels_file
    self.num_skipped_instance = 0

  def ProcessInputDir(self, input_dir):
   """Traverses all subdirectories, assuming their names are 3-letters."""
   for filename in sorted(glob.iglob(os.path.join(input_dir, "*"))):
      self.ProcessSingleFile(filename)
   print "Num blacklisted instances skipped:", self.num_skipped_instance

  def ProcessSingleFile(self, filename):
    print """Extracts features from an input file using feature_extractors.""", filename
    base_filename = os.path.basename(filename)
    label = "L" if base_filename == "literal.txt" or "nonmet" in base_filename or "nomet" in base_filename else "M"
    for extractor in self.feature_extractors:
      extractor.BeginNewFile(base_filename)
    for line in codecs.open(filename, "r", "utf-8"):
      self._ProcessLine(label, base_filename, line)

  def _ProcessLine(self, label, base_filename, line):
    line_num, rel_type, instance_num, sub, verb, obj = self._ParseLine(line)
    instance = "_".join( (base_filename, unicode(line_num), rel_type, unicode(instance_num),
        unicode(sub), unicode(verb), unicode(obj), label) )
    if args.skip_subject_null_instances and sub.is_none:
      return
    if (base_filename, line_num, sub.word_index, verb.word_index, obj.word_index) in self.blacklisted_instances:
      self.num_skipped_instance += 1
      return
    feature_dict = {}
    for extractor in self.feature_extractors:
      feature_dict.update(extractor.ExtractFeaturesFromInstance(
          base_filename, line_num, rel_type, sub, verb, obj))
    self._WriteFeatures(instance, feature_dict)
    self._WriteLabel(instance, label)

  def _ParseLine(self, line):
    line = line.lower()
    line_num, rel_type, instance_num, sub, verb, obj = line.strip().split("\t")
    assert rel_type in ['svo', 'an'], rel_type
    line_num = int(line_num)
    instance_num = int(instance_num)
    sub = TurboWord(sub)
    verb = TurboWord(verb)
    obj = TurboWord(obj)
    return line_num, rel_type, instance_num, sub, verb, obj

  def _WriteFeatures(self, instance, feature_dict):
    """Saves features in Creg format."""
    features_str = json.dumps(feature_dict, sort_keys=True)
    self.features_file.write(u"{0}\t{1}\n".format(instance, features_str))

  def _WriteLabel(self, instance, label):
    """Saves label (responses) file in Creg format."""
    self.labels_file.write(u"{0}\t{1}\n".format(instance, label))


def LoadBlacklist(filename):
  result = set()
  if filename is not None and os.path.isfile(filename):
    for line in open(filename):
      # "literal.txt_941_32_banks_33_lend_L"
      tokens = line.strip().split('_')
      base_filename = tokens[0]
      line_num = int(tokens[1])
      sub_index = int(tokens[2])
      verb_index = int(tokens[4])
      obj_index = 999 if len(tokens) == 7 else int(tokens[6])
      result.add( (base_filename, line_num, sub_index, verb_index, obj_index) )
  return result


def main(argv):
  blacklisted_instances = LoadBlacklist(args.blacklisted_instances)
  instance_extractor = InstanceExtractor(feature_extractors,
      blacklisted_instances,
      codecs.open(args.features_filename, "w", "utf-8"),
      codecs.open(args.labels_filename, "w", "utf-8"))
  if args.input_dir is not None:
    instance_extractor.ProcessInputDir(args.input_dir)
  else:
    instance_extractor.ProcessSingleFile(args.input_file)


if __name__ == '__main__':
  main(sys.argv)
