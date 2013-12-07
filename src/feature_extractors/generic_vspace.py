#!/usr/bin/python

from __future__ import division
import codecs
import feature_extractor

class GenericVectorSpace(feature_extractor.FeatureExtractor):
  """Base abstract class for VSM representations."""

  def __init__(self, vectorSpaceUniqName, vectFileName, translation_dict):
    self.vectorSpaceUniqName = vectorSpaceUniqName
    self.translation_dict = translation_dict
    """ The format is: <word> <elem1> <elem2> ... <elem26>  """
    LineNum=0
    self.vectors = {}
    self.N = None
    for line in codecs.open(vectFileName, 'r', 'utf-8'):
      line = line.strip()
      LineNum = LineNum + 1
      toks = line.split()
      if self.N is None:
        self.N = len(toks) - 1
      if len(toks) != self.N + 1:
        raise Exception(u'Bad line # {}: {}'.format(LineNum, line))
      vect = [float(tok) for tok in toks[1:]]
      word = toks[0]
      self.vectors[word] = vect
      #print u'>> "{}"->{}'.format(word, vect)

  def _GetWords(self, word):
    if self.translation_dict is None:
      return [word]
    else:
      return self.translation_dict.Get(word)

  def _WordToFeature(self, word, role):
    result = {}
    words = self._GetWords(word.lower())

    avgVect = [0.0] * self.N

    count = 0
    for w in words:
      if w in self.vectors:
        count += 1
        vect = self.vectors[w]
        for i in range(self.N): 
          avgVect[i] += vect[i]

    if count > 0:
      for i in range(self.N):
        result['{}_feature_{}_{}'.format(self.vectorSpaceUniqName, role, i)] = avgVect[i] / count

    return result

