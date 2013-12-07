#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import codecs
import collections
import sys
import re

class Dictionary:
  def __init__(self, reverse_direction=False):
    self.dict = collections.defaultdict(set)
    self.reverse_direction = reverse_direction

  def Add(self, word, translation):
    if self.reverse_direction:
      word, translation = translation, word
    if not word.isalpha() or not translation.isalpha():
      return
    translation = translation.strip().lower()
    word = word.lower()
    self.dict[word].add(translation)

  def AddSet(self, word, translations):
    for translation in translations:
      self.Add(word, translation)

  def Get(self, word):
    return self.dict.get(word, [])

def LoadDictionary(filename, reverse_direction=False):
  '''Dictionary format a UTF-8 coded file:
  fr1,fr2,fr3,..,frN\ten1,en2,en3,en4,..,enM
  '''
  dict_obj = Dictionary(reverse_direction=reverse_direction)
  for line in codecs.open(filename, 'r', 'utf-8'):
    fr_line, en_line = line.strip().split("\t")
    en_words = [w.strip() for w in en_line.split(",")]
    fr_words = [w.strip() for w in fr_line.split(",")]
    for fr_word in fr_words:
      dict_obj.AddSet(fr_word, en_words)
  return dict_obj

DICT_CACHE={}
def GetDict(filename, reverse_direction=False):
  if (filename, reverse_direction) not in DICT_CACHE:
    DICT_CACHE[(filename, reverse_direction)] = LoadDictionary(
        filename, reverse_direction)
  return DICT_CACHE[(filename, reverse_direction)]
  
if __name__ == '__main__':
  print "This is a library."
  sys.exit(1)
