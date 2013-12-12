#!/usr/bin/env python2.7
#-*- coding: utf-8 -*-

import sys
import collections
import codecs
import argparse
from nltk.stem.wordnet import WordNetLemmatizer

parser = argparse.ArgumentParser()

parser.add_argument("--turbo_filename", required=True)
parser.add_argument("--out_file", default=None)
parser.add_argument("--filter_verbs_filename",
    help="Filename with verbs that should be processed. If not specified, process all verbs.")
parser.add_argument("--rel_type", default="SVO", help="Either SVO or AN")
args = parser.parse_args()

lemmatizer = WordNetLemmatizer()
 
class TurboWord:
  def __init__(self, line):
    tokens = line.strip().replace(u"�","?").split('\t')
    self.id = int(tokens[0])-1
    self.surface_form = tokens[1].split()[-1].lower()  # Only the last word.
    self.lemma = tokens[2].lower()
    self.pos_tag = tokens[3]
    if self.lemma in [u'-', u'_']:
      if self.pos_tag.startswith("V"):
        lemmatizer_pos = 'v'  
      elif  self.pos_tag.startswith("N"): 
        lemmatizer_pos = 'n'
      else:
        lemmatizer_pos = 'a' 
      self.lemma = lemmatizer.lemmatize(self.surface_form, lemmatizer_pos).lower()
    self.head = int(tokens[6])-1
    self.dep_rel = tokens[7]

  def __repr__(self):
    return u"{0} {1} {2} {3}".format(self.lemma, self.surface_form, self.pos_tag, self.id)

  def OutStr(self):
    return u"\t".join([self.surface_form, str(self.id)])

class Rel:
  def __init__(self, verb, noun):
    self.verb = verb
    self.noun = noun

class TurboSentence:
  def __init__(self, num_sentence, out_file, verb_filter):
    self.words = []
    self.num_sentence = num_sentence
    self.out_file = out_file
    self.verb_filter = verb_filter

  def AddWord(self, line):
    word = TurboWord(line)
    self.words.append(word)

  def FullSentence(self):
    return u" ".join([w.surface_form for w in self.words])

  def Write(self, rel_type, sub, verb, obj=None):
    instance_num = -1
    self.out_file.write(u"{}\t{}\t{}\t{}\t{}\t{}\n".format(
        self.num_sentence, rel_type, instance_num, sub, verb, obj))

  def SaveSVO(self):
    sub_rel, obj_rel = self.GetSVO()
    seen_verb_objects = set()
    for sub_r in sub_rel:
      sub = sub_r.noun
      verb = sub_r.verb
      if self.verb_filter and verb.lemma not in self.verb_filter:
        continue
      obj_list = obj_rel.get(sub_r.verb.id, None)
      if obj_list:
        for obj in obj_list:
          self.Write("svo", sub, verb, obj.noun)
          seen_verb_objects.add( (verb.id, obj.noun.id) )
      else:
        self.Write("svo", sub, verb)

    for verb_id, obj_rel_list in obj_rel.iteritems():
      for verb_obj_rel in obj_rel_list:
        verb, obj = verb_obj_rel.verb, verb_obj_rel.noun
        if (verb.id, obj.id) not in seen_verb_objects:
          if self.verb_filter and verb.lemma not in self.verb_filter:
            continue
          self.Write("svo", None, verb, obj)

  def GetSVO(self):
    sub_rel = []
    obj_rel = collections.defaultdict(list)
    subst_verb = dict([ (x.head, x.id)  for x in self.words if x.dep_rel == u'VC' ])
    subjects = [ x for x in self.words if x.dep_rel == u'SUB']
    for sub in subjects:
      if sub.surface_form.isalpha():        
        verb_idx = subst_verb.get(sub.head, sub.head)
        verb = self.words[verb_idx]
        if verb.surface_form.isalpha():
          sub_rel.append(Rel(verb, sub))

    objects = [ x for x in self.words if x.dep_rel == u'OBJ' ]
    for obj in objects:
      if obj.surface_form.isalpha():
        verb = self.words[obj.head]
        if verb.surface_form.isalpha():
          obj_rel[verb.id].append(Rel(verb, obj))
    return sub_rel, obj_rel

  def SaveAN(self):
    adjectives = [ x for x in self.words if x.dep_rel == u'NMOD' and x.pos_tag == u'JJ' ]
    for adj in adjectives:
      if adj.surface_form.isalpha():
        id = adj.head
        # There may be a chain of words between an adjective and the respective noun
        # The loop would terminate, e.g., by reaching the dep_rel == u'ROOT'
        while self.words[id].dep_rel in [u'PMOD', u'NMOD']: 
          id = self.words[id].head
        noun = self.words[id]
        if noun.pos_tag.startswith(u'NN') and adj.id < noun.id:
          self.Write('an', adj, None, noun)

def ParseTurboOutput(in_file, out_file, verb_filter, rel_type):
  num_sentence = 0
  sentence = TurboSentence(num_sentence, out_file, verb_filter)
  for line in in_file:
    if len(line.strip()) == 0:
      if rel_type == 'svo':
        sentence.SaveSVO()
      else:
        sentence.SaveAN()
      num_sentence += 1
      sentence = TurboSentence(num_sentence, out_file, verb_filter)
    else:
      sentence.AddWord(line)

def LoadFilterVerbs(filename):
  verbs = set()
  for line in codecs.open(filename, "r", "utf-8"):
    verbs.add(line.strip())
  return verbs

def main(argv):
  if args.out_file is not None:
    out_file = codecs.open(args.out_file, "w", 'utf-8')
  else:
    out_file = sys.stdout

  rel_type = args.rel_type.lower()
  if rel_type not in ['svo', 'an']:
    print "--rel_type must be either SVO or AN"
    sys.exit(1)

  if args.filter_verbs_filename:
    verb_filter = LoadFilterVerbs(args.filter_verbs_filename)
  else:
    verb_filter = None

  in_file = codecs.open(args.turbo_filename, 'r', 'utf-8')
  ParseTurboOutput(in_file, out_file, verb_filter, rel_type)

 
if __name__ == '__main__':
  main(sys.argv)

