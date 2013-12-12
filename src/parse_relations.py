#!/usr/bin/env python2.7
#-*- coding: utf-8 -*-

import sys
import collections
import codecs
import glob
import os
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("--input_dir", help="Directory with relation files")
parser.add_argument("--output_dir", help="Directory with results.")
parser.add_argument("--rel_type", help="Relation types (SVO or NN).")

args = parser.parse_args()

def FormatWord(word, i, type):
  return word + " " + word + " " + str(type) + " " + str(i)

def ProcessFileAN(in_filename, out_filename):
  out_file = codecs.open(out_filename, "w", "utf-8")
  for index, line in enumerate(codecs.open(in_filename, "r", "utf-8")):
    n1, n2 = line.strip().split()
    out_file.write(str(index) + '\tan\t-1\t' +  FormatWord(n1, 1, 'JJ') + '\tNone\t' + FormatWord(n2, 2, 'NN')+'\n')

def ProcessFileSVO(in_filename, out_filename):
  out_file = codecs.open(out_filename, "w", "utf-8")
  for index, line in enumerate(codecs.open(in_filename, "r", "utf-8")):
    tokens = line.strip().split()
    if len(tokens) != 3:
      continue
    n1, n2, n3 = tokens
    out_file.write(str(index) + '\tsvo\t-1\t' +  FormatWord(n1, 1, 'NN') + '\t' + FormatWord(n2, 2, 'VB') + '\t' + FormatWord(n3,3, 'NN')+'\n')

def main():
  for filename in glob.iglob(os.path.join(args.input_dir, "*")):
    basename = os.path.basename(filename)
    out_filename = os.path.join(args.out_dir, basename)
    if args.rel_type.lower() == 'an':
      ProcessFileAN(filename, out_filename)
    else:
      assert args.rel_type.lower() == 'svo', args.rel_type
      ProcessFileSVO(filename, out_filename)
 
if __name__ == '__main__':
  main()



